from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from io import BytesIO
from copy import deepcopy
import re
import fitz
from hashlib import md5
import streamlit as st

from langchain_core.documents.base import Document

class File(ABC): 
    def __init__(
        self, 
        name: str, 
        id: str, 
        metadata: Optional[Dict[str, Any]] = None,
        docs: Optional[List[Document]] = None
    ):
        self.name = name
        self.id = id 
        self.metadata = metadata or {}
        self.docs = docs or {}
    
    @classmethod
    @abstractmethod
    def from_file(cls, file: BytesIO, removed_words: List[str]) -> "File":
        """Create a file object holding information about the file"""
        pass
    
    def __repr__(self):
        return f"File(name={self.name}, id={self.id}, metadata={self.metadata})"

    def copy(self):
        return self.__class__(
            name=self.name, 
            id=self.id,
            docs=deepcopy(self.docs),
            metadata=deepcopy(self.metadata)
        ) 


def clean_doc(text: str, removed_words: List[str]) -> str:
    text = re.sub(r" +", " ", text).strip() # Replaces multiple spaces with a single space.
    text = re.sub(r"\n{2, }", "\n\n", text) # {2, }: match 2 or more consecutive newlines
    pattern = r"\b(?:" + "|".join(map(re.escape, removed_words)) + r")\b"
    # pattern = r"(?:" + "|".join(map(re.escape, removed_words)) + r")" 
    # (?:...): a non-capturing group, used to group regex without saving the match.
    # |: OR operator — matches any of the listed words.
    # Why use re.escape? To escape special characters in removed_words. For example, if removed_words contains C++, it becomes C\+\+.
    # \b means: Match only if the word has a space, punctuation, or start/end of string around it
    text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text

class PdfFile(File):
    @classmethod
    def from_file(cls, file: BytesIO, removed_words: List[str]) -> "PdfFile":
        
        with fitz.open(stream=file.read(), filetype="pdf") as pages: # rõ ràng code cũ không có cái này nhưng vẫn chạy được
            docs = []
            for i, page in enumerate(pages):
                text_blocks = page.get_text("blocks")
                texts = [ block[4] for block in text_blocks if len(block[4]) > 400 ] 
                # chỉ trích xuất các text block có độ dài > 400, tránh thu thập các block có độ dài quá ngắn và không có ý nghĩa 
                # thứ tự xuất hiện của các block trong list không giống với thứ tự xuất hiện của các block trong văn bản thật
                # vị thứ 4 mới chứa content của text block
                for x, text in enumerate(texts): 
                    text = clean_doc(text, removed_words)
                    doc = Document(page_content=text)
                    doc.metadata["page"] = i + 1
                    doc.metadata["block"] = x + 1
                    docs.append(doc)

        file.seek(0) # trỏ về lại phần đầu của file, vì con trỏ đã về cuối trong quá trình đọc file, mục đích vì sao thì mình không hiểu, bước đóng file nằm ở đâu
        return cls(
            name=file.name, 
            id=md5(file.read()).hexdigest(),
            docs=docs # ở đây docs chưa từng text box ở mỗi trang thuộc một file, các text box này phải có nội dung tối thiểu là 400 characters
        )
    
# file là BytesIO: objects are in-memory streams and are automatically cleaned up by Python's garbage collector when no longer referenced
# pages là sản phẩn của fitz.open() nên cần đóng lại

@st.cache_data(show_spinner=True)  
def read_files(files: List[BytesIO], removed_words: List[str]) -> List[File]:
    read_files = []
    # read_files chứa các instance về mỗi văn bản, mỗi instance chứa docs là một list các text block từ các page (thông tin định vị nằm trong metadata)
    for file in files:
        if file.name.lower().endswith(".pdf"):
            pdf_file = PdfFile.from_file(file, removed_words)
            read_files.append(pdf_file)
        else: 
            return NotImplementedError(f"This {file.name.split('.')[-1]} is not supported")
    return read_files