import streamlit as st 
import os 

def sidebar():
    with st.sidebar:
        # General guide section
        st.markdown(
            "## Cách sử dụng \n"
            "1. Nhập [OpenAI API Key](https://platform.openai.com/account/api-keys) của bạn vào bên dưới \n"
            "2. Chọn mô hình LLM \n"
            "3. Chọn hình thức tương tác \n"
        )

        # API Key input section
        api_key_input = st.text_input(
            label="OpenAI API Key", 
            type="password",
            placeholder="Nhập API key (sk-....)", 
            help="Bạn có thể đăng ký API key ở https://platform.openai.com/account/api-keys",
            value=os.environ.get("OPENAI_API_KEY", None)
            or st.session_state.get("OPENAI_API_KEY", None)
        )
        st.session_state["OPENAI_API_KEY"] = api_key_input

        st.markdown("------")

        if not api_key_input: 
            st.warning("Bạn cần nhập API key để sử dụng app")

        # Model options section
        llm_model = st.selectbox(
            label="Chọn LLM model",
            options=["gpt-4.1-nano", "gpt-4.1-mini", "gpt-4o-mini", "gpt-3.5-turbo"]
        )        
        st.session_state["LLM_MODEL"] = llm_model
