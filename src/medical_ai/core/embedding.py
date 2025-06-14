from typing import List
from langchain_core.documents.base import Document
from langchain_core.vectorstores.base import VectorStore
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
import streamlit as st



@st.cache_resource(show_spinner=True)    
def create_index(store_id: str, _docs: List[Document]) -> VectorStore:
    index = FAISS.from_documents(
        documents=_docs, 
        embedding=OpenAIEmbeddings()
    )
    return index

# store_id chỉ có vai trò trong quá trình cache_resource

