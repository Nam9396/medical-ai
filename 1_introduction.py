import streamlit as st 

st.title("Giới thiệu")

st.markdown("""
    ## Chào mừng đến với Ứng dụng MedAI!

    Chúng tôi rất vui được đồng hành cùng bạn trong hành trình khám phá và làm chủ nội dung văn bản một cách dễ dàng, hiệu quả và thông minh hơn. Ứng dụng này được phát triển dựa trên công nghệ Mô hình ngôn ngữ lớn (LLM), với mục tiêu hỗ trợ bạn tiếp cận, hiểu và sử dụng văn bản một cách linh hoạt, phục vụ cho học tập, làm việc hay nghiên cứu.

    ### 🎯 Mục đích của ứng dụng
    - Giúp người dùng hiểu sâu hơn nội dung của các văn bản phức tạp.
    - Tiết kiệm thời gian đọc và xử lý tài liệu.
    - Tạo ra các phiên bản văn bản phù hợp với nhu cầu sử dụng khác nhau.
    - Tra cứu và trả lời câu hỏi dựa trên cơ sở dữ liệu Pubmed.
    - Tương tác với mô hình LLM y khoa MedGemma từ Google.

    ### 🔧 Các chức năng chính
    - **Hỏi – Đáp về nội dung văn bản:** Đặt câu hỏi liên quan đến văn bản và nhận được câu trả lời chính xác, ngắn gọn, dựa trên nội dung bạn cung cấp.
    - **Viết lại văn bản ở dạng dễ đọc, dễ hiểu:** Viết lại các đoạn văn với ngôn ngữ dễ hiểu, ngắn gọn, có đề mục rõ ràng.
    - **Viết lại văn bản theo chủ đề:** Bạn cung cấp chủ đề, ứng dụng sẽ tìm trong văn bản những đoạn văn có nội dung phù hợp và viết lại theo cách dễ hiểu, ngắn gọn nhưng vẫn đầy đủ thông tin.
    - **Tra cứu Pubmed**: Tra cứu và xếp hạng mức độ liên quan của các bài báo từ Pubmed dựa trên câu hỏi.
    - **Hỏi đáp từ PMC**: Dựa trên câu hỏi của người dùng, ứng dụng tra cứu các bài báo có liên quan trên cơ sở dữ liệu Free Pubmed Central và tạo câu trả lời.
    - **MedGemma**: Hỏi đáp các vấn đề y khoa và chẩn đoán hình ảnh với mô hình MedGemma.
            
    ### 📝 Hướng dẫn sử dụng
    - Tải lên nội dung văn bản mà bạn muốn xử lý.
    - Chọn chức năng bạn cần: hỏi đáp, viết lại dễ hiểu, viết lại theo chủ đề hoặc tóm tắt.
    - Nhập thêm thông tin (nếu có) như câu hỏi cụ thể hoặc chủ đề mong muốn.
    - Nhấn "Thực hiện" và chờ trong giây lát để nhận kết quả từ ứng dụng.
                
    ### 🧑‍💻 Tác giả
    - Bs. Nguyễn Thành Nam
    - nguyenthanhnam9396@gmail.com
""")