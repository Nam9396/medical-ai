import streamlit as st 
import time

from core.entrez import entrez_esearch, efetch_pubmed_abstract
from graphs.rank_docs_graph import rank_docs_graph
from components.ui import display_general_error, display_retry_loop_error


st.title("PubMed Search")

st.markdown("""
1. Bạn nhập từ khóa cần tìm kiếm. 
2. Ứng dụng tra cứu cơ sở dữ liệu và tải về 200 bài báo đầu tiên. 
3. AI đọc tiêu đề và tóm tắt để lọc ra các bài báo có liên quan nhất. 
4. Ứng dụng trả về một danh sách ID của các bài báo. 
5. Copy paste các ID này vào ô tìm kiếm trên [website PubMed](https://pubmed.ncbi.nlm.nih.gov/) để tra cứu toàn văn.         
            
""")

user_query = st.text_input("Nhập từ khóa cần tìm kiếm", "pediatric autoimmune encephalitis")

doc_analyse_number = st.slider("Chọn số bài báo sẽ được phân tích", 10, 200, 20, help="Số lượng bài báo càng nhiều, thời gian phân tích càng lâu. Bạn cần xem xét giảm thời gian phân tích để tăng tốc độ phản hồi và thử được nhiều lần hơn.")

if st.button("Tìm kiếm") and user_query:
    
    with st.spinner("Đang tìm kiếm từ cơ sở dữ liệu ...", show_time=True): # Nếu phát sinh lỗi, spinner vẫn quay đến vô tận, làm sao để khắc phục
        try: 
            esearch_results = entrez_esearch(db="pubmed", term=user_query)
            with st.expander("Bước 1: Tổng quan kết quả tìm kiếm"):
                st.markdown("### Tổng quan")
                st.markdown(f"**Tổng số kết quả:** {esearch_results['Count']}")
                st.markdown(f"**Số kết quả thực sự trả về:** {esearch_results['RetMax']}")
                st.markdown(f"**Số kết quả sẽ được phân tích:** {doc_analyse_number}")
                st.markdown(f"**Phiên giải từ khóa từ PubMed:** {esearch_results['QueryTranslation']}")
        except Exception as e: 
            display_general_error(e=e, message="Phát sinh lỗi trong quá trình tìm kiếm từ PubMed. Xin thử lại sau vài phút.")
        id_list = esearch_results["IdList"]

    with st.spinner("Đang trích xuất thông tin ...", show_time=True):     
        articles = None
        for attempt in range(3):
            try:
                articles = efetch_pubmed_abstract(id=id_list[:doc_analyse_number])
                with st.expander(f"Bước 2: Kết quả tìm kiếm ban đầu (hiển thị 10/{doc_analyse_number})"):
                    for article in articles[:10]:
                        title = article.metadata["title"]
                        id = article.metadata["article_ids"]["pubmed"]
                        st.write(f"PubMed ID: {id} - {title}")
                break
            except Exception as e:
                display_retry_loop_error(e)
                time.sleep(2)

        if articles is None:
            st.error(f"[FAILED] Thất bại sau 3 lần thử. Tải lại chương trình.")
            st.stop()

    with st.spinner("Đang phân tích và xếp hạng mức độ liên quan ...", show_time=True):
        try:
            response = rank_docs_graph(
                query=user_query, 
                documents=articles
            )
            with st.expander("Bước 3: Các bài báo có liên quan"):
                st.markdown("### Danh sách PubMed ID")
                st.markdown(f'Tổng số PubMed ID: {len(response["relevant_docs_ids"])}')
                st.markdown("Bạn có thể copy và dán các ID bên dưới vào ô tìm kiếm trên [website PubMed](https://pubmed.ncbi.nlm.nih.gov/) .")
                st.markdown(", ".join([ id.strip("'") for id in response["relevant_docs_ids"] ]))
                st.markdown("-----")
                for doc in response["relevant_docs"]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(doc["content"].page_content)
                        st.markdown(f'**PubMed ID:** {doc["content"].metadata["article_ids"]["pubmed"]}')
                        if doc["content"].metadata["article_ids"].get("pmc", ""):
                            st.markdown("**PMC free article**")
                        else: 
                            st.markdown(f'**DOI:** {doc["content"].metadata["article_ids"].get("doi", "Không có mã doi")}')
                    with col2:
                        st.markdown(f'**Điểm số liên quan:** {doc["relevance_score"]}')
                        st.markdown(f'**Lý do:** {doc["justification"]}')
                    st.markdown("-----")

        except Exception as e: 
            display_general_error(e=e, message="Đã xảy ra lỗi trong quá trình phân tích bài báo. Xin thử lại sau vài phút.")
    
        
        






