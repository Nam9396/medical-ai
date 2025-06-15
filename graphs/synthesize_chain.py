from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from setting import synthesize_prompt_template_1, synthesize_prompt_template_2, get_synthesize_model


synthesize_prompt = PromptTemplate(
    template=synthesize_prompt_template_2, 
    input_variables=["topic", "documents"]
)
synthesize_model = get_synthesize_model()
synthesize_chain = synthesize_prompt | synthesize_model | StrOutputParser()


