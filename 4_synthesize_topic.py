import streamlit as st
import time 

from core.parsing import read_files
from core.chunking import chunk_files
from graphs.synthesize_topic_graph import synthesize_topic_graph
from components.ui import display_general_error, display_general_warning, display_retry_loop_error

st.title("Tổng hợp theo chủ đề")

st.markdown("Bạn đang gặp khó khăn khi đọc một đoạn văn bản quá dài, quá học thuật, hoặc không phù hợp với đối tượng người đọc? Bạn cung cấp chủ đề, ứng dụng sẽ tìm những đoạn văn có nội dung phù hợp và viết lại toàn bộ một cách dễ đọc, dễ hiểu nhưng vẫn đầy đủ thông tin.")


uploaded_files = st.file_uploader(
    label="Tải lên file .pdf", 
    type=["pdf"], 
    accept_multiple_files=True
)

if not uploaded_files: 
    st.stop()

if "process_docs" not in st.session_state:
    st.session_state.process_docs = False

with st.expander(label="Loại bỏ các từ/cụm từ không cần thiết khỏi văn bản"):
    removed_words = st.text_area(
        label="Nhập các từ/cụm từ không cần thiết",
        label_visibility='hidden',
        placeholder="Mỗi từ/cụm từ cần được phân cách bởi dấu '/', ví dụ: bài báo/văn bản/tác giả. Bạn cũng có thể nhập các cụm từ dài, ví dụ: trong bài viết này.../các kết quả cho thấy...",
        disabled= True if st.session_state.process_docs else False
    )
    removed_words = [text.lower() for text in removed_words.split("/")]

col1, col2, col3 = st.columns(3)

def process_docs():
    st.session_state.process_docs = True
    st.toast("Đang đọc và làm sạch văn bản ...")
    if "INPUT_FILES" not in st.session_state:
        try: 
            st.session_state["INPUT_FILES"] = read_files(files=uploaded_files, removed_words=removed_words)
        except Exception as e:
            display_general_error(e=e, message="Phát sinh lỗi trong quá trình đọc File. Xin đảm bảo file không bị gián đoạn hoặc mã hóa")

def reset_all():
    st.session_state.process_docs = False
    if "INPUT_FILES" in st.session_state:
        del st.session_state["INPUT_FILES"]

with col2:
    if not st.session_state.process_docs:
        st.button(
            "Thực hiện",
            use_container_width=True, 
            on_click=process_docs   
        )
    else:
        st.button(
            "Đặt lại", 
            use_container_width=True, 
            on_click=reset_all
        )

if "INPUT_FILES" not in st.session_state:
    st.stop()

chunks_store = chunk_files(st.session_state["INPUT_FILES"], chunk_size=300, chunk_overlap=50)

if len(chunks_store["docs"]) == 0:
    display_general_warning(message="File không có nội dung. Bấm đặt lại, xóa file cũ và tải lên có nội dung.")

with st.form(key='qa_form'):
        query = st.text_area("Nhập chủ đề cần tổng hợp")
        submit = st.form_submit_button("Thực hiện")

if submit and query:
    
    with st.spinner("Đang tìm kiếm các nội dung liên quan và tổng hợp ...", show_time=True):
        
        response = None
        
        for attempt in range(3):
            try:
                response = synthesize_topic_graph(query=query, documents=chunks_store["docs"])
                break
            except Exception as e:
                display_retry_loop_error(e)
                time.sleep(2)
            
        if response is None:
            st.error(f"[FAILED] Thất bại sau 3 lần thử. Tải lại chương trình.")
            st.stop()

        st.write(response["synthesized_doc"])

        with st.expander("Trích dẫn các đoạn văn bản"):
            for doc in response["relevant_docs"]:
                metadata_values = list(doc.metadata.values())
                st.write(doc.page_content)
                st.write(f"name: {metadata_values[0]} - page: {metadata_values[1]} - block: {metadata_values[2]}")
                st.markdown("------")
