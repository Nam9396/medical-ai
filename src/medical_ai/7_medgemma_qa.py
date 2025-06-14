import streamlit as st
import json
from core.hugging_face import medgemma_chat_model, medgemma_endpoint, medgemma_gradio_client

st.title("MedGemma Q&A")

st.markdown("MedGemma [google/medgemma-4b-it](https://huggingface.co/google/medgemma-4b-it) là mô hình ngôn ngữ lớn được Google phát triển và đào tạo bằng các văn bản và hình ảnh y khoa. MedGemma có khả năng trả lời các câu hỏi y khoa và phân tích hình ảnh (Xquang, CTscan, MRI, da liễu, mô học).")

with st.expander("Hướng dẫn sử dụng MedGemma"):
    st.markdown("Sử dụng MedGemma có tính phí (20000đ/giờ). Do đó, chỉ kích hoạt mô hình khi cần và bất hoạt ngay khi có thể.")
    endpoint_status = medgemma_endpoint.fetch().status
    if endpoint_status == "running":
        st.success("Mô hình đã sẵn sàng, bạn có thể bắt đầu tương tác. Nhớ bất hoạt mô hình khi không sử dụng ở trang MedGemma Setting.")
    else: 
        st.warning("Mô hình chưa được kích hoạt, chuyển sang trang MedGemma Setting để kiểm tra tình trạng và kích hoạt mô hình")
        st.stop()

# with st.expander("Hướng dẫn sử dụng MedGemma"):
#     st.markdown("Mô hình MedGemma được thực thi trên nền tảng Hugging Face Space. Bạn có thể phải đợi để mô hình xử lý dữ liệu. Nếu gặp lỗi, xin vui lòng tải lại trang sau vài phút.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is heart failure?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Đang xử lý ...", show_time=True):

            if len(st.session_state.messages) >= 10:
                st.session_state.messages = st.session_state.messages[-8]

            # response = medgemma_gradio_client.predict(
            #     messages=json.dumps([
            #         {"role": m["role"], "content": [{"type": "text", "text": m["content"]}]}
            #         for m in st.session_state.messages
            #     ]),
            #     temperature=0.7,
            #     api_name="/predict"
            # )

        
            stream = medgemma_chat_model.stream([
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ])
            response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})

