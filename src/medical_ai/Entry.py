import streamlit as st
from components.sidebar import sidebar


st.set_page_config(layout="wide")

introduction_page = st.Page("1_introduction.py", title="Giới thiệu", icon=":material/emoji_people:")
qa_rag_page = st.Page("2_qa_rag.py", title="Q&A", icon=":material/forum:")
rewrite_overall_page = st.Page("3_rewrite_overall.py", title="Viết lại văn bản", icon=":material/edit_square:")
rewrite_topic_page = st.Page("4_synthesize_topic.py", title="Tổng hợp theo chủ đề", icon=":material/tag:")
pubmed_search_page = st.Page("5_search_pubmed.py", title="Pubmed Search PMIDs", icon=":material/search:")
pmc_search_answer_page = st.Page("6_search_answer_pmc.py", title="PMC Search and Answer", icon=":material/book_4:")
med_gemma_page = st.Page("7_medgemma_qa.py", title="Google MedGemma Q&A", icon=":material/local_hospital:")
image_diagnosis = st.Page("8_image_diagnosis.py", title="MedGemma Image Diagnosis", icon=":material/add_photo_alternate:")
medgemma_setting_page = st.Page("9_medgemma_setting.py", title="MedGemma Setting", icon=":material/settings:")

pg = st.navigation([
    introduction_page, 
    qa_rag_page, 
    rewrite_overall_page, 
    rewrite_topic_page, 
    pubmed_search_page, 
    pmc_search_answer_page,
    med_gemma_page,
    image_diagnosis, 
    medgemma_setting_page
])

sidebar() # sidebar nằm ở vị trí này sẽ không được gọi do pg.run() đã chuyển sang trang khác 

pg.run()


