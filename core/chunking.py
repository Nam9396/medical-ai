from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document
import streamlit as st
import core.parsing as parsing
from core.parsing import File
from typing import List



def hash_funcs():

    def return_id(file: File) -> str:
        return file.id
    
    classes = vars(parsing).values()
    subclasses = [ subclass for subclass in classes
        if isinstance(subclass, type) and issubclass(subclass, File) and subclass is not File             
    ]
    return { subclass: return_id for subclass in subclasses }


# @st.cache_data(show_spinner=True, hash_funcs=hash_funcs())
def chunk_files(files: List[File], chunk_size: int, chunk_overlap: int) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap, 
        separators=[r"\n\n", r"\n", r"(?<=[.?!])\s+"],  # Order matters! Larger breaks should come first
        is_separator_regex=True
    )

    docs = []

    for file in files:
        for doc in file.docs: # mỗi doc là một text box ở từng trang
            chunks = text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                final_doc = Document(page_content=chunk)
                final_doc.metadata["file_name"] = file.name
                final_doc.metadata["page"] = doc.metadata.get("page", 1)
                final_doc.metadata["block"] = doc.metadata.get("block", 1)
                final_doc.metadata["chunk"] = i + 1
                docs.append(final_doc)
                
    chunks_store = {
        "store_id": "".join([file.id for file in files]), 
        "docs": docs
    }

    return chunks_store


def chunk_pmc_article(article: Document, chunk_size: int, chunk_overlap: int) -> List[Document]:
    
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap, 
        separators=[r"\n\n", r"\n", r"(?<=[.?!])\s+"],  # Order matters! Larger breaks should come first
        is_separator_regex=True
    )

    chunks = text_splitter.split_text(article.page_content) 
    # bản thân của page_content không phải là các text box như trong file pdf, nó là một chuỗi các string trích xuất từ định dạnh xml và kết nối với nhau bởi các khoảng trắng (xem entrez get_body_text)
    # do đó, sẽ không có thông tin về page để truy xuất đúng đoạn văn, người dùng phải tự down bài báo về và tìm kiếm

    chunks_store = []

    for i, chunk in enumerate(chunks):
        sub_doc = Document(page_content=chunk)
        sub_doc.metadata["title"] = article.metadata["title"]
        sub_doc.metadata["pmcid"] = article.metadata["pmcid"]
        chunks_store.append(sub_doc)
    
    # ở đây metadata của chunk chỉ cần chứa title và PMCID để truy xuất bài báo, không cần chứa các trường dữ liệu khác như abstract, relevance_score, justification

    return chunks_store
            

