import streamlit as st
import time 

from core.parsing import read_files
from core.chunking import chunk_files
from core.embedding import create_index_with_cache
from graphs.qa_graph import qa_graph
from components.ui import display_general_error, display_general_warning, display_retry_loop_error

st.title("Hỏi đáp về văn bản")

st.markdown("Bạn có một văn bản dài và cần nhanh chóng tìm câu trả lời cho những câu hỏi cụ thể? Hãy sử dụng chức năng Hỏi – Đáp. Chức năng này được xây dựng dựa trên công nghệ RAG (Retrieval-Augmented Generation) – một phương pháp kết hợp giữa truy xuất thông tin (retrieval) và sinh văn bản tự động (generation).")

if "input_files" not in st.session_state:
    st.session_state["input_files"] = None

def handle_uploaded_files_change():
    if not st.session_state["input_files"]:
        st.session_state["input_files"] = None
    else: 
        del st.session_state["input_files"]

uploaded_files = st.file_uploader(
    label="Tải lên một hoặc nhiều file pdf.", 
    help="Chỉ xử lý file chứa nội dung có thể bôi đen và copy paste. Không chấp nhận file pdf chứa nội dung là hình ảnh scan.",
    type=["pdf"], 
    accept_multiple_files=True,
    on_change=handle_uploaded_files_change
)

def process_docs():
    try: 
        st.session_state["input_files"] = read_files(files=uploaded_files, removed_words="")
        st.toast("Hoàn thành đọc và làm sạch văn bản.")
    except Exception as e:
        display_general_error(e=e, message="Phát sinh lỗi trong quá trình đọc file. Xin đảm bảo file không bị gián đoạn, không mã hóa.")

col1, col2, col3 = st.columns(3)

with col2:
    st.button(
        "Xử lý văn bản",
        use_container_width=True, 
        on_click=process_docs,
        disabled=True if not uploaded_files else False
    )

if not uploaded_files or not st.session_state["input_files"]:
    st.stop()

chunks_store = chunk_files(st.session_state["input_files"], chunk_size=300, chunk_overlap=50)

if len(chunks_store["docs"]) == 0:
    display_general_warning(message="File không có nội dung hoặc nội dung là hình ảnh scan. Bấm đặt lại, xóa file cũ và tải lên file có nội dung.")

with st.form(key='qa_form'):
        query = st.text_area("Đặt câu hỏi về văn bản")
        submit = st.form_submit_button("Thực hiện")


if submit and query:

    with st.spinner("Đang xử lý văn bản và trả lời ... Vui lòng đợi trong giây lát⏳", show_time=True):     
        try: 
            vector_store = create_index_with_cache(store_id=chunks_store["store_id"], _docs=chunks_store["docs"])
        except Exception as e: 
            display_general_error(e=e, message="Phát sinh lỗi trong quá trình lập chỉ mục nội dung. Nguyên nhân: file bị lỗi hoặc liên quan đến mạng.")
            
        graph = qa_graph(vector_store=vector_store)

        response = None

        for attempt in range(3):
            try:
                response = graph.invoke({ "question": query })
                break
            except Exception as e:
                display_retry_loop_error(e)
                time.sleep(2)
        
        if response is None:
            st.error(f"[FAILED] Thất bại sau 3 lần thử. Bấm tải lại chương trình sau vài phút.")
            st.stop()
    
        st.markdown("#### CÂU TRẢ LỜI")

        st.markdown(response["answer"])

        st.markdown("---")

        with st.expander("TRÍCH DẪN NGUỒN TÀI LIỆU"):
            for doc in response["context"]:
                metadata_values = list(doc.metadata.values())
                metadata_info = f"**File: {metadata_values[0]} - Trang: {metadata_values[1]} - Đoạn: {metadata_values[2]}**"        
                st.markdown(metadata_info)
                st.write(doc.page_content)
                st.markdown("-----")

