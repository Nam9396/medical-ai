from langchain_core.prompts import PromptTemplate
from langchain_core.documents.base import Document

import streamlit as st
import xml.etree.ElementTree as ET
from pydantic import BaseModel,Field
from Bio import Entrez
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Literal, Optional, Dict, Literal
import http.client
import time
from setting import rank_prompt_template, get_rank_model

from core.entrez import get_iter_text, get_body_text
from core.chunking import chunk_pmc_article

Entrez.email = "nguyenthanhnam9396@gmail.com"
Entrez.api_key = "b8ec89560a7de7899dc38d867a60972dc708"


rank_prompt = PromptTemplate(
    template=rank_prompt_template, 
    input_variables=["question", "paragraph"]
)

class RelevanceEvaluation(BaseModel):
    relevance_score: Literal[0, 1, 2, 3, 4, 5] = Field(
        description="Relevance score of the article, from 0 (not relevant) to 5 (completely relevant)"
    )
    justification: str = Field(
        description="Explanation for why the relevance score was assigned"
    )

rank_model = get_rank_model()
structured_llm = rank_model.with_structured_output(RelevanceEvaluation)
rank_chain = rank_prompt | structured_llm


def efetch_raw_article(id: str) -> str:
    handle = Entrez.efetch(
        db="pmc",
        id=id,
        rettype="full",
        retmode="xml",
    )
    data = handle.read()
    handle.close()
    return data


def get_article_abstract(data: str):
    entry = ET.fromstring(data)
    title_elem = entry.find(".//article-title")
    title = get_iter_text(title_elem, "Không tìm thấy tiêu đề")
    abstract_elems = entry.findall(".//abstract")
    abstract = "\n\n".join([ get_iter_text(elem, "Không tìm thấy tóm tắt") for elem in abstract_elems ]) if abstract_elems else "Không tìm thấy tóm tắt"
    # desired_ids = {"pmcid", "pmid", "doi"}
    pmcid = None
    for id_elem in entry.findall(".//article-id"):
        id_type = id_elem.attrib.get("pub-id-type", "No id detected")
        if id_type == "pmcid":
            pmcid = id_elem.text
    doc = Document(page_content="")
    doc.metadata = {
        "title": title,
        "abstract": abstract,
        "pmcid": pmcid
    }
    return doc     


def rank_article(question: str, doc: Document) -> Optional[Document]:
    response = rank_chain.invoke({
        "question": question,
        "paragraph": doc.metadata["title"] + "\n\n" + doc.metadata["abstract"]
    })
    if response.relevance_score >= 4:
        # doc.metadata["relevance_score"] = response.relevance_score
        # doc.metadata["justification"] = response.justification
        return doc
    else: 
        return None


def get_article_fulltext(data: str, doc: Document) -> Document:
    entry = ET.fromstring(data)
    body_elem = entry.find(".//body")
    body_text = get_body_text(body_elem, "Không tìm thấy nội dung chính, hoặc nội dung là hình ảnh.")
    doc.page_content = body_text
    return body_text, doc


def process_one_pmc_article(question: str, id: str) -> Optional[Tuple[Dict, List]]:
    raw_obj = efetch_raw_article(id=id)
    abstract_obj = get_article_abstract(data=raw_obj)
    rank_obj = rank_article(question=question, doc=abstract_obj)
    if rank_obj is not None: 
        body_text, doc = get_article_fulltext(data=raw_obj, doc=rank_obj)
        if body_text == "Không tìm thấy nội dung chính, hoặc nội dung là hình ảnh.":
            return None
        else: 
            chunk_store = chunk_pmc_article(article=doc, chunk_size=300, chunk_overlap=50) 
            return rank_obj, chunk_store
    else: 
        return None


def retry_process_article(question: str, id: str, retries=3, delay=2) -> Optional[Tuple]:
    for attempt in range(retries):
        try:
            return process_one_pmc_article(question, id)
        except http.client.IncompleteRead as e:
            print(f"[Attempt {attempt + 1}] IncompleteRead for ID {id}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            print(f"[Attempt {attempt + 1}] General error for ID {id}: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    print(f"[FAILED] Could not process ID {id} after {retries} attempts.")
    return None # cho phép return None, bỏ qua bài báo hoàn toàn nếu thất bại sau 3 lần xử lí

# Nên đặt rety theo từng task chứ không phải toàn bộ quá trình parallel. Nếu như vậy khi retry ta sẽ bắt đầu lại toàn bộ từ đầu và add vào list các kết quả đã được xử lý


def orchestrate_all_in_parallel(question: str, id_list: List[str]):
    results = []
    empty_container = st.empty()
    empty_container.progress(0)
    total = len(id_list)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(retry_process_article, question, id): id
            for id in id_list
        }

        for i, future in enumerate(as_completed(futures)):
            id = futures[future]
            try:
                result = future.result()
                results.append(result)
                # status_text.text(f"Đang xử lý bài báo PMCID: {id}")
            except Exception as e:
                st.toast(f"Lỗi khi xử lý bài báo PMCID {id}: {e}")
            # progress_bar.progress((i + 1) / total)
            empty_container.progress((i + 1) / total)
            
    empty_container.empty()
    return results 



# document_form = {
#     "metadata": { 
#         "title": str,
#         "abstract": str, tạm bỏ
#         "pmid": str,
#         "relevance_score": int, tạm bỏ
#         "justification": str, tạm bỏ
#     }
# }