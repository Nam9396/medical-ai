import streamlit as st
import base64
import json
from core.hugging_face import medgemma_chat_model, medgemma_endpoint, medgemma_gradio_client
from components.ui import display_general_error

st.title("MedGemma Image Q&A")

st.markdown("MedGemma [google/medgemma-4b-it](https://huggingface.co/google/medgemma-4b-it) là mô hình ngôn ngữ lớn được Google phát triển và đào tạo bằng các văn bản và hình ảnh y khoa. MedGemma có khả năng trả lời các câu hỏi y khoa và phân tích hình ảnh (Xquang, CTscan, MRI, da liễu, mô học).")

with st.expander("Hướng dẫn sử dụng MedGemma"):
    st.markdown("Sử dụng MedGemma có tính phí (20000đ/giờ). Do đó, chỉ kích hoạt mô hình khi cần và bất hoạt ngay khi có thể. Tải lên ảnh từ thiết bị hoặc nhập đường dẫn.")
    endpoint_status = medgemma_endpoint.fetch().status
    if endpoint_status == "running":
        st.success("Mô hình đã sẵn sàng, bạn có thể bắt đầu tương tác. Nhớ bất hoạt mô hình khi không sử dụng ở trang MedGemma Setting.")
    else: 
        st.warning("Mô hình chưa được kích hoạt, chuyển sang trang MedGemma Setting để kiểm tra tình trạng và kích hoạt mô hình")
        st.stop()

image_source = st.radio(
    "Chọn hình thức tải hình ảnh", 
    ["Tải file từ thiết bị", "Nhập đường dẫn đến hình ảnh"], 
    index=0
)

if image_source == "Tải file từ thiết bị":
    file = st.file_uploader("Tải lên hình ảnh", type=["jpg", "jpeg", "png"])
else:
    image_url = st.text_input("Nhập đường dẫn đến hình ảnh", help="Đường dẫn có dạng https:// --- .jpg/png/jpeg")

with st.form(key='qa_form'):
    query = st.text_area("Đặt câu hỏi về hình ảnh", value="Describe this image and suggest a diagnosis.")
    submit = st.form_submit_button("Thực hiện")

image_message = None

# đoạn mã này hoạt động tốt với gradio api
# if image_source == "Tải file từ thiết bị":
#     image_message = [
#         {
#             "role": "user",
#             "content": [
#                 {"type": "image", "base64": base64.b64encode(file.read()).decode("utf-8") if file is not None else None },
#                 {"type": "text", "text": query},
#             ],
#         },
#     ]
# else:
#     image_message = [
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "image",
#                     "image": image_url, # key có thể là image hoặc url, nhưng không chấp nhận image_url (với processor), với tonkenizer thì chấp nhận image_url nhưng trả kết quả về không tối ưu # https://huggingface.co/docs/transformers/chat_templating_multimodal#transformers.ProcessorMixin
#                 },
#                 {"type": "text", "text": query},
#             ],
#         },
#     ]


# đoạn mã này hoạt động tốt với Inference Endpoint
if image_source == "Tải file từ thiết bị":
    image_message = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(file.read()).decode('utf-8') if file is not None else None}"}},
                {"type": "text", "text": query}            
            ],
        },
    ]
else:
    image_message = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": query},
            ],
        },
    ]

# image_source_status = image_message[0]["content"][0].get("image", None) or image_message[0]["content"][0].get("base64", None)

image_source_status = image_message[0]["content"][0]["image_url"].get("url", None)

with st.expander("Xem nội dung prompt"):
    st.write(image_message)

if submit:
    if not query or not image_source_status:
        st.warning("Bạn cần nhập đủ nguồn hình ảnh và câu hỏi")
        st.stop()
    else:
        with st.spinner("Đang xử lý ...", show_time=True):
            try: 
                response = medgemma_chat_model.stream(image_message)
                st.write_stream(response)
            except Exception as e: 
                display_general_error(e=e, message="Không thể trích xuất dữ liệu hình ảnh từ file hoặc đường dẫn, xin thử lại với file hoặc đường dẫn khác.")

        # with st.spinner("Vui lòng đợi trong giây lát ...", show_time=True):
        #     response = medgemma_gradio_client.predict(
        #         messages=json.dumps(image_message), 
        #         temperature=0.7,
        #         api_name="/predict"
        #     )
        #     st.write(response)


    
   


