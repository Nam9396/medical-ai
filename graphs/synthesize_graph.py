from langchain_core.documents.base import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import operator
from typing import List, Annotated, TypedDict, Dict, Literal
from pydantic import BaseModel,Field
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from setting import synthesize_prompt_template_1, synthesize_prompt_template_2, get_synthesize_model, rank_prompt_template, get_rag_model


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

rank_model = get_rag_model()
structured_llm = rank_model.with_structured_output(RelevanceEvaluation)
rank_chain = rank_prompt | structured_llm


synthesize_prompt = PromptTemplate(
    template=synthesize_prompt_template_2, 
    input_variables=["topic", "documents"]
)
synthesize_model = get_synthesize_model()
synthesize_chain = synthesize_prompt | synthesize_model | StrOutputParser()


def synthesize_graph(query: str, documents: List[Document]) -> Dict:
    
    class RankState(TypedDict):
        question: str
        document: Document

    class OverallState(TypedDict):
        question: str
        initial_docs: List[Document]
        relevant_docs: Annotated[List[Document], operator.add]
        # irrelevant_docs: Annotated[List[Document], operator.add]
        synthesized_doc: str

    def rank_docs(state: RankState):
        response = rank_chain.invoke({
            "question": state["question"],
            "paragraph": state["document"].page_content
        })
        if response.relevance_score >= 3:
            return {
                "relevant_docs": [state["document"]] # lưu ý ở đây response cần đặt trong một [...]
            }
        # else: 
        #     return {
        #         "irrelevant_docs": [state["document"]] # lưu ý ở đây response cần đặt trong một [...]
        #     }

    def initial_parallelization(state: OverallState):
        return [
            Send("rank_docs", {"question": state["question"], "document": doc}) for doc in state["initial_docs"]
        ]

    def rewrite_docs(state: OverallState):
        combined_doc = "\n\n".join(doc.page_content for doc in state["relevant_docs"])
        synthesized_doc = synthesize_chain.invoke({
            "topic": state['question'], 
            "documents": combined_doc
        })
        return {
            "synthesized_doc": synthesized_doc
        }

    graph = StateGraph(OverallState)
    graph.add_node("rank_docs", rank_docs)
    graph.add_node("rewrite_docs", rewrite_docs)

    graph.add_conditional_edges(START, initial_parallelization, ["rank_docs"])
    graph.add_edge("rank_docs", "rewrite_docs")
    graph.add_edge("rewrite_docs", END)

    app = graph.compile()

    response = app.invoke({
        "question": query,
        "initial_docs": documents
    })

    return response

    