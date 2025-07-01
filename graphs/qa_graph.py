from langchain_core.prompts import PromptTemplate
from langchain_core.vectorstores.base import VectorStore
from langgraph.graph import StateGraph, START
from langchain_core.documents.base import Document
from typing import TypedDict, List
from setting import rag_prompt_template, get_rag_model


prompt = PromptTemplate(
    template=rag_prompt_template, 
    input_variables=["retrieved_documents", "user_query"]
)

def qa_graph(
    vector_store: VectorStore
):
    
    rag_model = get_rag_model()
    
    class State(TypedDict):
        question: str 
        context: List[Document]
        answer: str
        
    def retrieve(state: State):
        retrieved_docs = vector_store.similarity_search(
            state["question"], 
            k=20
        )
        return { "context": retrieved_docs }
    
    def generate(state: State):
        context_content = "\n\n".join([doc.page_content for doc in state["context"]])
        message = prompt.invoke({
            "user_query": state["question"], 
            "retrieved_documents": context_content
        })
        response = rag_model.invoke(message)
        return { "answer": response.content }
    
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])

    graph_builder.add_edge(START, 'retrieve')

    graph = graph_builder.compile()

    return graph