import streamlit as st
import os
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# https://smith.langchain.com/hub/rajkstats/science-product-rag-prompt-non-reasoning
rag_prompt_template_1 = """
You are a scientific research assistant with expertise in retrieving and synthesizing scientific information.

CONTEXT:
{retrieved_documents}

QUERY: {user_query}

Using ONLY the information in the CONTEXT above, provide a comprehensive answer to the QUERY. Include relevant scientific data, methodologies, and findings from the retrieved documents. If the information is not present in the context, state that you don't have sufficient information to answer.

Format your response with appropriate headings and bullet points for clarity. Cite specific information from the context where relevant.
"""


# https://smith.langchain.com/hub/rajkstats/science-product-rag-prompt-reasoning
# rag_prompt_template_2 = """
# You are a scientific research assistant with expertise in analyzing scientific information.

# CONTEXT:
# {retrieved_documents}

# QUERY: {user_query}

# First, identify the key scientific concepts and data points in the CONTEXT that relate to the QUERY.
# Then, analyze how these concepts connect to form a comprehensive answer.
# Finally, synthesize your findings into a detailed response.

# Think step by step through the scientific principles involved. Identify any gaps in the retrieved information and note where additional research might be needed.

# Use ONLY information from the provided CONTEXT. If the information is not sufficient, acknowledge the limitations of your response.
# """

rag_prompt_template_2 = """
You are a scientific research assistant with expertise in analyzing scientific information.

### 📋 Instructions:
- ONLY use the information from the documents provided below.
- DO NOT include any information not found in the documents, even if it is commonly known.
- If the documents do not contain sufficient information, reply with:
  > "⚠️ Insufficient information in the provided documents to generate a meaningful synthesis."

### 📋 Guidelines:
1. First, identify the key scientific concepts and data points in the CONTEXT that relate to the QUERY.
2. Then, analyze how these concepts connect to form a comprehensive answer.
3. Finally, synthesize your findings into a detailed response.

Think step by step through the scientific principles involved. Identify any gaps in the retrieved information and note where additional research might be needed.

CONTEXT:
{retrieved_documents}

QUERY: {user_query}
"""


rank_prompt_template = """
You are an expert assistant tasked with evaluating how relevant a paragraph is in answering a specific question.

Please read the **Question** and the **Paragraph**, and then return a structured result with:

1. `relevance_score`: an integer between 0 and 5 indicating how well the paragraph answers the question:
    - 0: Not relevant at all
    - 1: Slightly relevant
    - 2: Somewhat relevant
    - 3: Moderately relevant
    - 4: Very relevant
    - 5: Completely relevant

2. `justification`: a short explanation of why you assigned that score.

Your response must match the expected format of a structured object with these two fields.

---

**Question**: {question}

**Paragraph**: {paragraph}
"""


rewrite_prompt_template = """
Rewrite the following document to be easier to read and more concise.
- Reorganize paragraphs in this document if that improves clarity.
- Break paragraphs into a bulleted or numbered list if that improves clarity.
- Remove any redundant or overly complex phrasing.
- Keep the original meaning intact.
- Create a representation title for each rewrite paragraph if needed.

Input document:
{document}     
"""


synthesize_prompt_template_1 = """
Using the list of documents provided below, create a new, original piece of content focused on the following topic:

Topic: {topic}

Guidelines:
- Synthesize key insights, facts, or arguments from the documents to support the topic.
- Organize the content in a logical structure, using headings or bullet points where appropriate.
- Use clear, concise language. Avoid jargon or overly complex phrasing.
- Ensure the new content is cohesive and flows naturally.
- Do not copy any document verbatim; rephrase and combine ideas as needed.
- You may provide a suggested title for the new content.

Source Documents:
{documents}
"""


synthesize_prompt_template_2 = """
Using the list of documents provided below, create a new, original piece of content focused on the following topic:

**Topic**: {topic}

### 📋 Instructions:
- ONLY use the information from the documents provided below.
- DO NOT include any information not found in the documents, even if it is commonly known.
- If the documents do not contain sufficient information, reply with:
  > "⚠️ Insufficient information in the provided documents to generate a meaningful synthesis."

### 📋 Guidelines:
1. Synthesize key insights, facts, or arguments from the documents to support the topic.
2. **Suggested Title** at the top.
3. Organize the content in a logical structure, using **headings, bullet points**, or **numbered sections** as appropriate.
4. Ensure the content is **cohesive** and flows naturally between sections.
5. Use clear, concise language. Avoid jargon or overly complex phrasing.
6. Do not copy any document verbatim; **rephrase** and combine ideas as needed.
7. ✅ If applicable, include a **summary table** capturing the main ideas, comparisons, or clinical factors mentioned. The table should be simple, informative, and relevant to the topic.

---
📚 **Source Documents**:
{documents}
"""


question_to_query_prompt_template = """
You are a biomedical search assistant specialized in crafting precise PubMed search queries. 

Your task is to convert a user's natural language question into a **valid and effective** PubMed query. Use combinations of:
- Boolean operators (AND, OR, NOT),
- MeSH terms (if appropriate),
- Field tags like [Title/Abstract] or [MeSH Terms] or [All Fields].

⚠️ Important Guidelines:
- DO NOT create made-up or overly long quoted phrases unless you're sure they are valid MeSH terms or commonly indexed phrases.
- Instead of quoting complex phrases (e.g., "autoimmune encephalitis, pediatric"), split them into simpler concepts using AND/OR.
- Use parentheses to organize logic clearly.
- Use synonyms to broaden coverage if appropriate.
- Apply filters like humans, language, or age only when clearly implied by the question.

User Question:
{user_question}

PubMed Query:
"""

@st.cache_resource(show_spinner=True)
def get_rag_model():
    return ChatOpenAI(
        model=st.session_state.get("LLM_MODEL", "gpt-4.1-mini"),
        api_key=OPENAI_API_KEY,
        temperature=0.2,
        top_p=0.9,
        presence_penalty=0.1,
        frequency_penalty=0.2
    )

@st.cache_resource(show_spinner=True)
def get_rank_model():
    return ChatOpenAI(
        model=st.session_state.get("LLM_MODEL", "gpt-4.1-mini"),
        api_key=OPENAI_API_KEY, 
        temperature=0.2,
        top_p=0.9, 
        presence_penalty=0.1,
        frequency_penalty=0.2
    )

@st.cache_resource(show_spinner=True)
def get_rewrite_model():
    return ChatOpenAI(
        model=st.session_state.get("LLM_MODEL", "gpt-4.1-mini"),
        api_key=OPENAI_API_KEY, 
        temperature=0.7,
        top_p=0.9, 
        presence_penalty=0.1,
        frequency_penalty=0.2
    )

@st.cache_resource(show_spinner=True)
def get_synthesize_model():
    return ChatOpenAI(
        model=st.session_state.get("LLM_MODEL", "gpt-4.1-mini"),
        api_key=OPENAI_API_KEY, 
        temperature=0.7,
        top_p=0.9, 
        presence_penalty=0.1,
        frequency_penalty=0.2
    )

@st.cache_resource(show_spinner=True)
def get_question_to_query_model():
    return ChatOpenAI(
        model=st.session_state.get("LLM_MODEL", "gpt-4.1-mini"),
        api_key=OPENAI_API_KEY, 
        temperature=0.2,
        top_p=0.9, 
        presence_penalty=0.1,
        frequency_penalty=0.2
    )
