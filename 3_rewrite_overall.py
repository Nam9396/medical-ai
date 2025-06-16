import streamlit as st
import time 

from core.parsing import read_files
from core.chunking import chunk_files
from graphs.rewrite_overall_graph import overall_rewrite_graph
from components.ui import display_general_error, display_general_warning, display_retry_loop_error

st.title("Viết lại văn bản")

st.markdown("Bạn đang gặp khó khăn khi đọc một đoạn văn bản quá dài, quá học thuật? Chức năng Viết lại văn bản sẽ giúp bạn chuyển đổi nội dung thành phiên bản dễ hiểu với bố cục rõ ràng.")

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

with st.spinner("Đang phân tích và tổng hợp ... Vui lòng đợi trong giây lát⏳", show_time=True):
    
    response = None
    
    for attempt in range(3):
        try:
            response = overall_rewrite_graph(documents=chunks_store["docs"])
            break
        except Exception as e:
            display_retry_loop_error(e)
            time.sleep(2)
    
    if response is None:
        st.error(f"[FAILED] Thất bại sau 3 lần thử. Tải lại chương trình.")
        st.stop()

    for doc in response["summaries"]:
        st.write(doc["content"])
        st.markdown(doc["metadata_info"])
        st.markdown("------")  
