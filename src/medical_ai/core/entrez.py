from Bio import Entrez
from typing import Dict, List
import xml.etree.ElementTree as ET
import xml.dom.minidom

from langchain_core.documents.base import Document

ncbi_api_key = "b8ec89560a7de7899dc38d867a60972dc708"

def get_iter_text(elem, default: str = "Không tìm thấy nội dung") -> str:
    return " ".join(elem.itertext()).strip() if elem is not None and elem.itertext() else default
    # itertext() trích xuất tất cả text ở tất cả các level, ngoài, trong, sau. Nếu chắp nối bằng " " string cuối cùng có cấu trúc đúng nhất nhưng mất tính hierarchical. Để duy trì tính hierarchical, chắp nối bằng "\n\n", lúc này các cấu trúc con như (p < 0.01) với p nằm trong tag <italic> sẽ trông kì cục

def get_text(elem, default: str = "Không tìm thấy nội dung") -> str:
    return elem.text.strip() if elem is not None and elem.text else default
    # .text chỉ trả về string đầu tiên trong element, có nghĩa là nó không trả về string của child element và string nằm sau đó

def get_body_text(elem, default: str = "Không tìm thấy nội dung chính", exclude_tags: List =None) -> str:
    if elem is None:
        return default
    
    if exclude_tags is None:
        exclude_tags = ["sup", "xref", "table"]

    def extract_text(node):
        if node.tag in exclude_tags:
            return ""
        text_parts = [node.text or ""]
        for child in node:
            text_parts.append(extract_text(child))
            if child.tail:
                text_parts.append(child.tail)
        return " ".join(text_parts)

    result = extract_text(elem).strip()

    return result if result else default


def entrez_esearch(
    db: str,
    term: str, 
    userhistory: str ='y',
    retstart: int = 0,
    retmax: int = 200, 
    sort: str = "relevance",
    user_email: str = 'nguyenthanhnam9396@gmail.com', 
) -> Dict:
    
    Entrez.email = user_email
    raw = Entrez.esearch(db=db, term=term, userhistory=userhistory, retstart=retstart, retmax=retmax, sort=sort)
    results = Entrez.read(raw)
    raw.close()
    return results


def efetch_pubmed_abstract(
    id: str, 
    retstart: int = 0,
    retmax: int = 20, 
    user_email: str = 'nguyenthanhnam9396@gmail.com',
) -> List[Dict]:
    
    Entrez.email = user_email

    articles = []

    for i in range(0, len(id), 20):
        batch_ids = id[i:i + 20]
        id_str = ", ".join([ i.strip("'") for i in batch_ids])

        raw = Entrez.efetch(db="pubmed", id=id_str, retstart=retstart, retmax=retmax, rettype="abstract", retmode="xml")
        tree = ET.fromstring(raw.read())
        raw.close()
        for entry in tree.findall(".//PubmedArticle"):
            title_elem = entry.find(".//ArticleTitle")
            title = get_iter_text(title_elem, "Không tìm thấy tiêu đề")
            abstract_elems = entry.findall(".//Abstract")
            abstract = "\n\n".join([ get_iter_text(elem, "Không tìm thấy tóm tắt") for elem in abstract_elems ]) if abstract_elems else "Không tìm thấy tóm tắt"
            desired_ids = {"pubmed", "pmc", "doi"}
            article_ids = {}
            for id_elem in entry.findall(".//ArticleId"):
                id_type = id_elem.attrib.get("IdType", "No id detected")
                if id_type in desired_ids and id_elem.text:
                    article_ids[id_type] = id_elem.text
            doc = Document(page_content=f"{title}\n\n{abstract}")
            doc.metadata = {
                "title": title,
                "article_ids": article_ids
            }
            articles.append(doc)     
    
    return articles


def efetch_pmc_abstract(
    id: str, 
    retstart: int = 0,
    retmax: int = 20, 
    user_email: str = 'nguyenthanhnam9396@gmail.com',
) -> List[Dict]:
    
    Entrez.email = user_email

    Entrez.api_key = ncbi_api_key

    articles = []

    for i in range(0, len(id), 20):
        batch_ids = id[i:i + 20]
        id_str = ",".join([ i.strip("'") for i in batch_ids])

        raw = Entrez.efetch(db="pmc", id=id_str, retstart=retstart, retmax=retmax, rettype="", retmode="")
        tree = ET.fromstring(raw.read())
        raw.close()
        for entry in tree.findall(".//article"):
            title_elem = entry.find(".//article-title")
            title = get_iter_text(title_elem, "Không tìm thấy tiêu đề")
            abstract_elems = entry.findall(".//abstract")
            abstract = "\n\n".join([ get_iter_text(elem, "Không tìm thấy tóm tắt") for elem in abstract_elems ]) if abstract_elems else "Không tìm thấy tóm tắt"
            desired_ids = {"pmcid", "pmid", "doi"}
            article_ids = {}
            for id_elem in entry.findall(".//article-id"):
                id_type = id_elem.attrib.get("pub-id-type", "No id detected")
                if id_type in desired_ids and id_elem.text:
                    article_ids[id_type] = id_elem.text

            doc = Document(page_content=f"{title}\n\n{abstract}")
            doc.metadata = {
                "title": title,
                "article_ids": article_ids
            }
            articles.append(doc)     

    return articles


def print_full_text(
    db: str, 
    id: str, 
    retstart: int = 0,
    retmax: int = 50, 
    user_email: str = 'nguyenthanhnam9396@gmail.com',
):
    
    Entrez.email = user_email

    articles = []

    for i in range(0, len(id), 50):
        batch_ids = id[i:i + 50]
        id_str = ",".join([ i.strip("'") for i in batch_ids])

        raw = Entrez.efetch(db=db, id=id_str, retstart=retstart, retmax=retmax, rettype="", retmode="")
        xml_str = raw.read().decode("utf-8")
        dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ")
        articles.append(pretty_xml)
        raw.close()
    return articles
    
    