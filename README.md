# 🔮 Thầy Tư Online - AI Bói Toán Tâm Linh

![Thầy Tư Banner](https://res.cloudinary.com/dkeupjars/image/upload/v1765298289/agent/thay-tu-online-banner_bodf9j.png)

[![Live Demo](https://img.shields.io/badge/🔮%20Live%20Demo-HuggingFace%20Spaces-FFD700?style=for-the-badge&logo=huggingface)](https://huggingface.co/spaces/nconghau/thay-tu-online)

**"Thiên cơ bất khả lộ... nhưng Thầy Tư thì có thể!"**

**Thầy Tư Online** là một trợ lý AI đậm chất văn hóa Việt Nam, chuyên về bói toán, tử vi và tư vấn tâm linh. Được xây dựng trên nền tảng **Google GenAI** và **Agent Developer Kit (ADK)**, Thầy Tư không chỉ trả lời thông minh mà còn mang đậm phong thái của một ông thầy bói miền Tây dí dỏm, chân chất.

---

## ✨ Tính Năng Nổi Bật

### 1. ☯️ Gieo Quẻ & Tư Vấn Tâm Linh (AI Persona)
*   Trò chuyện tự nhiên với persona "Ông già Nam Bộ".
*   Giải đáp thắc mắc về vận hạn, tình duyên, gia đạo, công việc.
*   Phong cách hài hước, thân thiện nhưng vẫn giữ được sự "linh thiêng".

### 2. � Lá Số Tử Vi Khoa Học
*   Tự động lập và phân tích biểu đồ **Radar Chart** 5 phương diện:
    *   Thân Mệnh (Sức khỏe, bản lĩnh)
    *   Tài Lộc (Tiền bạc)
    *   Quan Lộc (Sự nghiệp)
    *   Tình Duyên (Gia đạo)
    *   Phúc Đức (May mắn)
*   Thuật toán tính toán dựa trên **Can Chi**, **Ngũ Hành Nạp Âm** và các **Sao chiếu mệnh** thực tế (không random).

### 3. 🔢 Thần Số Học (Numerology)
*   Tính toán chuẩn **Pythagoras**.
*   Các chỉ số chi tiết:
    *   **Số Chủ Đạo (Life Path)**: Đường đời và sứ mệnh.
    *   **Số Thái Độ**: Cách phản ứng với thế giới.
    *   **Năm Cá Nhân**: Dự báo vận hạn từng năm.

### 4. 🌌 Cung Hoàng Đạo (Zodiac)
*   Tra cứu thông tin 12 chòm sao phương Tây (Western Zodiac).
*   Cung cấp dữ liệu chi tiết về: Nguyên tố, Sao chiếu mệnh, Tính cách, Hợp/Khắc.

### 5. 🛡️ Bảo Mật & An Toàn
*   **Chống Spam**: Giới hạn tần suất 20 câu hỏi/phút (Rate Limiting).
*   **Bảo vệ dữ liệu**: Input validation chống tấn công, ẩn API Keys.
*   **Riêng tư**: Không lưu trữ thông tin cá nhân lâu dài.

---

## 🛠️ Công Nghệ Sử Dụng

*   **Core AI**: Google Gemini 2.5 Flash (qua `google-genai`).
*   **Framework**: Google Agent Developer Kit (ADK), Flask (Python).
*   **Frontend**: HTML5, CSS3 (Responsive), JavaScript (Vanilla).
*   **Security**: Flask-Limiter, Dotenv.
*   **Charting**: Chart.js (vẽ biểu đồ Radar).

---

## 🚀 Cài Đặt & Chạy Dự Án

### Yêu cầu
*   Python 3.10 trở lên.
*   Google Gemini API Key.

### Các bước thực hiện

1.  **Clone dự án**:
    ```bash
    git clone https://github.com/your-username/thay-tu-online.git
    cd thay-tu-online
    ```

2.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Cấu hình môi trường**:
    *   Tạo file `.env` từ file mẫu (nếu có) hoặc tự tạo:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key_here
    SESSION_SECRET=your_secret_key
    FLASK_DEBUG=true
    ```

4.  **Chạy ứng dụng**:
    ```bash
    python app.py
    ```
    *   Truy cập: `http://localhost:7860`

---



## 📝 Lưu Ý
*   Kết quả chỉ mang tính chất tham khảo và giải trí.
*   "Đức năng thắng số" - Thầy Tư luôn khuyên con cháu sống tốt, làm việc thiện thì vận mệnh tự khắc sẽ hanh thông.

---

**@nconghau25 ❤️  ☕ v1.0.0**
