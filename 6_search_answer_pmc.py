import streamlit as st 
import time

from core.entrez import entrez_esearch
from components.ui import display_general_error, display_retry_loop_error
from core.process_article import orchestrate_all_in_parallel
from core.embedding import create_index_no_cache

from graphs.question_query_chain import question_to_query_chain
from graphs.qa_graph import qa_graph
from graphs.synthesize_chain import synthesize_chain


st.title("Free PubMed Central QA")

st.markdown("""
1. Bạn nhập câu hỏi. 
2. AI chuyển đổi câu hỏi thành PubMed Query.
3. Ứng dụng tra cứu cơ sở dữ liệu và tải về 200 bài báo đầu tiên. 
4. AI đọc tiêu đề và tóm tắt để chọn ra những bài báo có liên quan.
5. AI đọc toàn văn các bài báo và tìm kiếm thông tin cần thiết để trả lời câu hỏi. 
6. Bên cạnh đó, ứng dụng cũng cung cấp nguồn văn bản trích dẫn.  

**Lưu ý**: Chỉ tải, xử lý và trả lời câu hỏi dựa trên các bài báo từ cơ sở dữ liệu [Free PubMed Central]((https://pmc.ncbi.nlm.nih.gov/)). Ứng dụng không thao tác trên các bài báo PubMed phải trả phí.     
            
""")

user_question = st.text_input("Nhập câu hỏi")

doc_analyse_number = st.slider("Chọn số bài báo sẽ được phân tích", 10, 200, 100, help="Số lượng bài báo càng nhiều, thời gian phân tích càng lâu. Bạn cần xem xét giảm thời gian phân tích để tăng tốc độ phản hồi và thử được nhiều lần hơn.")

if st.button("Tìm kiếm") and user_question:
    
    with st.spinner("Chuyển đổi câu hỏi thành PubMed query", show_time=True):
        query = question_to_query_chain.invoke({ "user_question": user_question })
        with st.expander("Bước 1: Chuyển đổi câu hỏi thành PubMed query"):
            st.write(query)

    with st.spinner("Đang tìm kiếm từ Free PubMed Central ...", show_time=True): 
        try: 
            esearch_results = entrez_esearch(db="pmc", term=query)
            id_list = esearch_results["IdList"]
            id_string = ", ".join(id.strip("'") for id in id_list) 
            with st.expander("Bước 2: Tổng quan kết quả tìm kiếm"):
                st.markdown("### Tổng quan")
                st.markdown(f"**Tổng số kết quả:** {esearch_results['Count']}")
                st.markdown(f"**Số kết quả thực sự trả về:** {esearch_results['RetMax']}")
                st.markdown(f"**Số kết quả sẽ được phân tích:** {doc_analyse_number}")
                st.markdown(f"**Phiên giải từ khóa từ Pubmed:** {esearch_results['QueryTranslation']}")
                st.markdown("Bạn có thể copy và dán các ID bên dưới vào ô tìm kiếm của [PubMed Central (PMC)](https://pmc.ncbi.nlm.nih.gov/).")
                st.markdown(f'{id_string}')  
        except Exception as e: 
            display_general_error(e=e, message="Phát sinh lỗi trong quá trình tìm kiếm từ PubMed Central (PMC). Xin thử lại sau vài phút.")

    with st.spinner("Đang tải và đánh giá các bài báo ...", show_time=True):
        relevant_articles = []
        articles_chunk_store = []

        results = orchestrate_all_in_parallel(question=user_question, id_list=id_list[:doc_analyse_number])

        for result in results:
            if result is not None:
                relevant_articles.append(result[0])
                articles_chunk_store.extend(result[1])
        
    if len(relevant_articles) == 0:
            st.warning("Sau đánh giá, không có bài báo nào phù hợp hoặc nội dung văn bản là hình ảnh. Hãy thử bấm tải lại, tăng số lượng bài báo được xử lý hoặc dùng từ khóa khác.")
            st.stop()

    with st.expander("Bước 3: Tổng quan các bài báo phù hợp"):
        st.write(f"Có {len(relevant_articles)} bài báo phù hợp trong tổng số {doc_analyse_number} kết quả")
        for index, article in enumerate(relevant_articles):
            title = article.metadata["title"]
            pmcid = article.metadata["pmcid"]
            st.write(f"{index + 1}. {title} - PubMed Central ID: {pmcid}")
        
    with st.spinner("Đang lập chỉ mục ...", show_time=True):
        try: 
            vector_store = create_index_no_cache(docs=articles_chunk_store)
            with st.expander("Bước 4: Lập chỉ mục truy xuất thành công"):
                st.write("Chỉ mục được dùng để truy xuất câu trả lời")
        except Exception as e: 
            display_general_error(e=e, message="Phát sinh lỗi trong quá trình lập chỉ mục tài liệu. Xin thử lại sau vài phút.")
        
    with st.spinner("Trả lời câu hỏi ...", show_time=True):
        graph = qa_graph(vector_store=vector_store)

        response = None
        
        for attempt in range(3):
            try:
                response = graph.invoke({ "question": user_question })
                break
            except Exception as e:
                display_retry_loop_error(e)
                time.sleep(2)
        
        if response is None:
            st.error(f"[FAILED] Thất bại sau 3 lần thử. Tải lại chương trình.")
            st.stop()

        st.markdown("#### CÂU TRẢ LỜI")
        st.markdown(response["answer"])
        st.markdown("---")
        
        with st.expander("Trích dẫn nguồn tài liệu"):
            for doc in response["context"]:
                metadata_info = f"**Tên: {doc.metadata['title']} - PubMed Central ID: {doc.metadata['pmcid']}**"        
                st.markdown(metadata_info)
                st.write(doc.page_content)
                st.markdown("-----")
    
    with st.spinner("Viết bài tổng hợp ngắn ...", show_time=True):
        retrieved_docs = vector_store.similarity_search(
            user_question, 
            k=20
        )

        combined_doc = "\n\n".join(doc.page_content for doc in retrieved_docs)

        response = None

        for attempt in range(3):
            try:
                response = synthesize_chain.invoke({ "topic": user_question, "documents": combined_doc })
                break
            except Exception as e:
                display_retry_loop_error(e)
                time.sleep(2)
        
        if response is None:
            st.error(f"[FAILED] Thất bại sau 3 lần thử. Tải lại chương trình.")
            st.stop()

        st.markdown("#### BÀI TỔNG HỢP NGẮN")
        st.markdown(response)
        st.markdown("---")    

        with st.expander("Dẫn nguồn thông tin"):
            for doc in retrieved_docs:
                metadata_info = f"**Tên: {doc.metadata['title']} - PubMed Central ID: {doc.metadata['pmcid']}**"        
                st.markdown(metadata_info)
                st.write(doc.page_content)
                st.markdown("-----")






    
        
        






