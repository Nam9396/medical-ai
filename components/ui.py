import streamlit as st
from streamlit.logger import get_logger
from typing import NoReturn


logger = get_logger(__name__)

def display_general_error(e: Exception, message: str) -> NoReturn:
    st.error(message)
    st.error(f"{e.__class__.__name__}: {e}")
    logger.error(f"{e.__class__.__name__}: {e}")
    st.stop()


def display_general_warning(message: str) -> NoReturn:
    st.warning(message)
    st.stop()


def display_retry_loop_error(e: Exception) -> NoReturn:
    st.toast(f"Lỗi thực thi. {e.__class__.__name__}: {e}. Thử lại sau 2 giây")
    logger.error(f"{e.__class__.__name__}: {e}")
    
    

def display_efetch_error(e: Exception) -> NoReturn: 
    st.error("Phát sinh lỗi trong quá trình tải dữ liệu bài báo khoa học.")
    st.error(f"{e.__class__.__name__}: {e}")
    logger.error(f"{e.__class__.__name__}: {e}")
    st.stop()

def display_general_error(e: Exception, message: str) -> NoReturn:
    st.error(message)
    st.error(f"{e.__class__.__name__}: {e}")
    logger.error(f"{e.__class__.__name__}: {e}")
    st.stop()