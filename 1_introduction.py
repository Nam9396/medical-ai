import streamlit as st 

st.title("Giới thiệu")

st.markdown("""
    ### Chào mừng đến với Ứng dụng MedAiVN!
    
    Ứng dụng được phát triển dựa trên công nghệ Mô hình ngôn ngữ lớn (LLM), với mục tiêu hỗ trợ bạn tiếp cận, đọc hiểu và sử dụng văn bản một cách hiệu quả; phục vụ cho học tập, làm việc hay nghiên cứu.

    ### Các chức năng chính
    - **Hỏi – Đáp về nội dung văn bản:** Đặt câu hỏi liên quan đến văn bản và nhận được câu trả lời chính xác, ngắn gọn, dựa trên nội dung bạn cung cấp.
    - **Viết lại văn bản ở dạng dễ đọc, dễ hiểu:** Viết lại các đoạn văn với ngôn ngữ dễ hiểu, ngắn gọn, có đề mục rõ ràng.
    - **Viết lại văn bản theo chủ đề:** Bạn cung cấp chủ đề, ứng dụng sẽ tìm trong văn bản những đoạn văn có nội dung phù hợp và viết lại theo cách dễ hiểu, ngắn gọn nhưng vẫn đầy đủ thông tin.
    - **Tra cứu PubMed**: Tra cứu và xếp hạng mức độ liên quan của các bài báo từ PubMed dựa trên câu hỏi.
    - **Hỏi đáp từ PubMed Central**: Dựa trên câu hỏi của người dùng, ứng dụng tra cứu các bài báo có liên quan trên cơ sở dữ liệu Free Pubmed Central và tạo câu trả lời.
    - **MedGemma**: Hỏi đáp các vấn đề y khoa và chẩn đoán hình ảnh với mô hình [Google MedGemma](https://huggingface.co/google/medgemma-4b-it).
            
    ### Hướng dẫn sử dụng
    - Nhập OpenAI API key của bạn.
    - Tải lên nội dung văn bản muốn xử lý.
    - Chọn chức năng bạn cần: hỏi đáp, viết lại dễ hiểu, viết lại theo chủ đề hoặc tìm kiếm PubMed.
    - Nhập thêm thông tin (nếu có) như câu hỏi cụ thể hoặc chủ đề mong muốn.
    - Nhấn "Thực hiện" và chờ trong giây lát để nhận kết quả từ ứng dụng.
                
    ### Tác giả
    
    Bs. Nguyễn Thành Nam
    
    nguyenthanhnam9396@gmail.com
            
    ### Giới hạn
    - Chỉ xử lý nội dung pdf có thể bôi đen và copy paste. Không xử lý nội dung pdf là hình ảnh scan.
    - Phản hồi từ LLM có thể thay đổi qua các lần thử khác nhau. Nếu phản hồi không đúng như mong muốn, hãy thử lại nhiều lần.
    - LLM có thể tự tạo câu trả lời với nội dung không xuất phát từ văn bản được cung cấp (hallucination). Ứng dụng đã hạn chế nguy cơ này thông qua các kĩ thuật prompting.
    - Các thao tác sử dụng dịch vụ bên ngoài như tra cứu PubMed/PubMed Central hoặc tương tác với MedGemma có thể gặp lỗi nếu kết nối internet không ổn định. Nếu phát sinh lỗi, xin thử lại chương trình sau vài phút.
    - Tất cả các tác vụ đều phát sinh chi phí: 
        + Chi phí ChatGPT API. 
        + Chi phí Hugging Face Inference Endpoints.
            
""")

st.markdown("### Danh mục các câu lệnh (Prompt)")

st.markdown("""
##### Hỏi đáp với ngữ cảnh được cung cấp (Retrieval-Augmented Generation - RAG)
              
You are a scientific research assistant with expertise in analyzing scientific information.

CONTEXT:
{retrieved_documents}

QUERY: {user_query}

First, identify the key scientific concepts and data points in the CONTEXT that relate to the QUERY.
Then, analyze how these concepts connect to form a comprehensive answer.
Finally, synthesize your findings into a detailed response.

Think step by step through the scientific principles involved. Identify any gaps in the retrieved information and note where additional research might be needed.

Use ONLY information from the provided CONTEXT. If the information is not sufficient, acknowledge the limitations of your response.

**📋 Instructions:**
- ONLY use the information from the provided CONTEXT.
- DO NOT include any information not found in the CONTEXT, even if it is commonly known.
- If the CONTEXT do not contain sufficient information, reply with:
  > "⚠️ Insufficient information in the provided CONTEXT to generate a meaningful synthesis."
""")

st.markdown("---")

st.markdown("""
##### Viết lại văn bản
            
Rewrite the following document to be easier to read and more concise.
- Reorganize paragraphs in this document if that improves clarity.
- Break paragraphs into a bulleted or numbered list if that improves clarity.
- Remove any redundant or overly complex phrasing.
- Keep the original meaning intact.
- Create a representation title for each rewrite paragraph if needed.

Input document:
{document}     
""")

st.markdown("---")

st.markdown("""
##### Tổng hợp theo chủ đề
            
Using the list of documents provided below, create a new, original piece of content focused on the following topic:

**Topic**: {topic}

**📋 Instructions:**
- ONLY use the information from the documents provided below.
- DO NOT include any information not found in the documents, even if it is commonly known.
- If the documents do not contain sufficient information, reply with:
  > "⚠️ Insufficient information in the provided documents to generate a meaningful synthesis."

**📋 Guidelines:**
1. Synthesize key insights, facts, or arguments from the documents to support the topic.
2. **Suggested Title** at the top.
3. Organize the content in a logical structure, using **headings, bullet points**, or **numbered sections** as appropriate.
4. Ensure the content is **cohesive** and flows naturally between sections.
5. Use clear, concise language. Avoid jargon or overly complex phrasing.
6. Do not copy any document verbatim; **rephrase** and combine ideas as needed.
7. ✅ If applicable, include a **summary table** capturing the main ideas, comparisons, or clinical factors mentioned. The table should be simple, informative, and relevant to the topic.

📚 **Source Documents**:
{documents}
""")

st.markdown("---")

st.markdown("""
##### Đánh giá mức độ liên quan của văn bản với chủ đề            

You are an expert assistant tasked with evaluating how relevant a paragraph is in answering a specific question.

Please read the **Question** and the **Paragraph**, and then return a structured result with:

1. `relevance_score`: an integer between 0 and 5 indicating how well the paragraph answers the question:
    - 0: Not relevant at all
    - 1: Slightly relevant
    - 2: Somewhat relevant
    - 3: Moderately relevant
    - 4: Very relevant
    - 5: Completely relevant

2. `justification`: a short explanation of why you assigned that score.

Your response must match the expected format of a structured object with these two fields.

**Question**: {question}

**Paragraph**: {paragraph}
""")

st.markdown("---")

st.markdown("""
##### Chuyển đổi câu hỏi thành PubMed query            

You are a biomedical search assistant specialized in crafting precise PubMed search queries. 

Your task is to convert a user's natural language question into a **valid and effective** PubMed query. Use combinations of:
- Boolean operators (AND, OR, NOT),
- MeSH terms (if appropriate),
- Field tags like [Title/Abstract] or [MeSH Terms] or [All Fields].

⚠️ Important Guidelines:
- DO NOT create made-up or overly long quoted phrases unless you're sure they are valid MeSH terms or commonly indexed phrases.
- Instead of quoting complex phrases (e.g., "autoimmune encephalitis, pediatric"), split them into simpler concepts using AND/OR.
- Use parentheses to organize logic clearly.
- Use synonyms to broaden coverage if appropriate.
- Apply filters like humans, language, or age only when clearly implied by the question.

User Question:
{user_question}

PubMed Query:...
""")