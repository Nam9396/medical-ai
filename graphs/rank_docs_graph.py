from langchain_core.documents.base import Document
from langchain_core.prompts import PromptTemplate

import operator
from typing import List, Annotated, TypedDict, Dict, Literal
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from setting import rank_prompt_template, get_rank_model

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


def rank_docs_graph(query: str, documents: List[Document]) -> Dict:

    class RankState(TypedDict):
        question: str
        document: Document

    class OverallState(TypedDict):
        question: str
        initial_docs: List[Document]
        relevant_docs: Annotated[List[Dict], operator.add]
        relevant_docs_ids: Annotated[List[str], operator.add]

    def rank_docs(state: RankState):
        response = rank_chain.invoke({
            "question": state["question"],
            "paragraph": state["document"].page_content
        })
        if response.relevance_score >= 4:
            return {
                "relevant_docs": [{
                    "content": state["document"], 
                    "relevance_score": response.relevance_score,
                    "justification": response.justification
                }], 
                "relevant_docs_ids": [ 
                    state["document"].metadata["article_ids"]["pubmed"] or 
                    state["document"].metadata["article_ids"]["pmid"] ]
            }

    def initial_parallelization(state: OverallState):
        return [
            Send("rank_docs", {"question": state["question"], "document": doc}) for doc in state["initial_docs"]
        ]

    graph = StateGraph(OverallState)
    graph.add_node("rank_docs", rank_docs)
    graph.add_conditional_edges(START, initial_parallelization, ["rank_docs"])
    graph.add_edge("rank_docs", END)

    app = graph.compile()

    response = app.invoke({
        "question": query,
        "initial_docs": documents
    })

    return response

    