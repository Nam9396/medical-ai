from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List, Annotated, TypedDict, Dict
from langchain_core.documents.base import Document
from langchain_core.language_models.base import BaseLanguageModel
import operator
from langgraph.constants import Send
from langgraph.graph import StateGraph, START, END
from setting import rewrite_prompt_template, get_rewrite_model


prompt = PromptTemplate(
    template=rewrite_prompt_template, 
    input_variables=["document"]
)

def overall_rewrite_chain(document: str, llm: BaseLanguageModel) -> str:
    rewrite_chain = prompt | llm | StrOutputParser()
    response = rewrite_chain.invoke({ "document": document })
    return response 

def overall_rewrite_graph(documents: List[Document]) -> Dict:
    
    llm = get_rewrite_model()

    class SummaryState(TypedDict):
        doc: Document

    class OverallState(TypedDict):
        contents: List[Document]
        summaries: Annotated[List[Dict], operator.add]

    def initial_parallelization(state: OverallState):
        return [ 
            Send("generate_summary", { "doc": doc }) for doc in state["contents"]
        ]

    def generate_summary(state: SummaryState):
        response = overall_rewrite_chain(document=state["doc"].page_content, llm=llm)
        metadata_values = list(state["doc"].metadata.values()) # nhớ là .values() trả về object dict_values([1, 2, 3])
        metadata_info = f"File: {metadata_values[0]} - Trang: {metadata_values[1]} - Đoạn: {metadata_values[2]}"        
        return { "summaries": [{
            "content": response, 
            "metadata_info": metadata_info
        }] }

    graph = StateGraph(OverallState)

    graph.add_node("generate_summary", generate_summary)

    graph.add_conditional_edges(START, initial_parallelization, ["generate_summary"])

    graph.add_edge("generate_summary", END)

    app = graph.compile()

    response = app.invoke(
        {"contents": documents},
    )

    return response