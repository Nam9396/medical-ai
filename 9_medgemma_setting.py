import streamlit as st
from core.hugging_face import medgemma_endpoint, ensure_endpoint_running

st.markdown("## KHỞI ĐỘNG MÔ HÌNH MEDGEMMA")
st.markdown("""
Sử dụng MedGemma gây phát sinh chi phí (20000đ/giờ). Do đó, bạn cần bất hoạt mô hình khi không sử dụng. Nếu không bất hoạt, mô hình sẽ tự động ngủ đông sau 15 phút không nhận yêu cầu từ người dùng.
- Bấm **Kiểm tra tình trạng mô hình** để biết mô hình có đang sẵn sàng hay không.
- Bấm **Bất hoạt mô hình** khi không sử dụng để không gây phát sinh chi phí.
- Quá trình **Kích hoạt mô hình** có thể mất từ 5 - 10 phút. 
- Nếu phát sinh lỗi, bấm tải lại trang và thử lại sau vài phút.
- Sau mỗi bước bất hoạt hay khởi động lại, bấm kiểm tra tình trạng để cập nhật trạng thái mới của mô hình.
""")

if "endpoint_status" not in st.session_state:
    st.session_state["endpoint_status"] = medgemma_endpoint.fetch().status

def check_endpoint_status():
    with st.spinner("Đang kiểm tra tình trạng mô hình ...", show_time=True):
        endpoint_status = medgemma_endpoint.fetch()
        endpoint_status = endpoint_status.status
        st.session_state["endpoint_status"] = endpoint_status

def resume_endpoint():
    with st.spinner("Đang kích hoạt mô hình, mất khoảng 5 phút ...", show_time=True):
        try:
            ensure_endpoint_running(timeout=420)
            st.toast(f"Mô hình đã sẵn sàng. Bấm kiểm tra tình trạng mô hình lại!")
        except TimeoutError:
            st.error("Không thể kích hoạt mô hình sau 5 phút. Xin bấm tải lại sau vài phút.")
            st.stop()

st.markdown(f"#### Tình trạng mô hình: {st.session_state['endpoint_status']}")

st.button("Kiểm tra tình trạng mô hình", on_click=check_endpoint_status)

endpoint_status_container = st.empty()

if st.session_state["endpoint_status"] == "running":
    endpoint_status_container.write("Bạn có thể chuyển sang trang MedGema Q&A để thao tác. Khi thao tác xong, quay lại trang cài đặt để bất hoạt mô hình.")
elif st.session_state["endpoint_status"] == "pending":
    endpoint_status_container.write("Mô hình đang khởi tạo xin đợi trong giây lát. Hãy bấm kiểm tra mô hình lại sau.")
else: 
    endpoint_status_container.write("Mô hình đang bất hoạt, bấm kích hoạt mô hình để khởi tạo.")
    with endpoint_status_container.container():
        st.button("Kích hoạt mô hình", on_click=resume_endpoint)

if st.button("Bất hoạt mô hình"):
    medgemma_endpoint.pause()
    st.toast(f"Mô hình đã bất hoạt. Bấm kiểm tra tình trạng mô hình lại!")


