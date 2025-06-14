from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from setting import question_to_query_prompt_template, get_question_to_query_model


question_to_query_prompt = PromptTemplate(
    template=question_to_query_prompt_template,
    input_variables=["user_question"]
)

question_to_query_model = get_question_to_query_model()

question_to_query_chain = question_to_query_prompt | question_to_query_model | StrOutputParser()

