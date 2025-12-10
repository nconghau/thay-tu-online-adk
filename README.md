---
title: Thay Tu Online
emoji: 🐠
colorFrom: green
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# 🔮 Thầy Tư Online - AI Bói Toán Tâm Linh

![Thầy Tư Banner](https://res.cloudinary.com/dkeupjars/image/upload/v1765298289/agent/thay-tu-online-banner_bodf9j.png)

[![Live Demo](https://img.shields.io/badge/🔮%20Live%20Demo-HuggingFace%20Spaces-FFD700?style=for-the-badge&logo=huggingface)](https://nconghau-thay-tu-online.hf.space/)

**"Thiên cơ bất khả lộ... nhưng Thầy Tư thì có thể!"**

**Thầy Tư Online** là một trợ lý AI đậm chất văn hóa Việt Nam, chuyên về bói toán, tử vi và tư vấn tâm linh. Được xây dựng trên nền tảng **Google GenAI** và **Agent Developer Kit (ADK)**, Thầy Tư không chỉ trả lời thông minh mà còn mang đậm phong thái của một ông thầy bói miền Tây dí dỏm, chân chất.

---

## ✨ Tính Năng Nổi Bật

### 1. 🌸 Tình Duyên & 🧧 Tài Lộc (Tư Vấn)
*   Chuyên trị các ca "ế lâu năm", tình duyên lận đận.
*   Dự đoán tài chính, cơ hội làm ăn, vận may (Lì xì đỏ).
*   Phong cách "Thầy Tư" chân chất, phán câu nào "thấm" câu đó.

### 2. 🕯️ Vận Hạn & 🎍 Tổng Quát
*   Soi vận hạn (Tam Tai, Thái Tuế...) để biết đường tránh né (Ngọn nến soi đường).
*   Xem tổng quan năm mới, định hướng công việc và cuộc sống.

### 3. ☯️ Lá Số Tử Vi Khoa Học
*   Tự động lập và phân tích biểu đồ **Radar Chart** 5 phương diện:
    *   Thân Mệnh (Sức khỏe, bản lĩnh)
    *   Tài Lộc (Tiền bạc)
    *   Quan Lộc (Sự nghiệp)
    *   Tình Duyên (Gia đạo)
    *   Phúc Đức (May mắn)
*   Thuật toán "Chính Phái": Tính toán dựa trên **Can Chi**, **Ngũ Hành**, **Sao Chiếu Mệnh** (không random).

### 4. 🔢 Số Chủ Đạo & Thần Số Học
*   **Số Chủ Đạo (Life Path)**: Tìm ra con số đường đời và sứ mệnh (Chuẩn Pythagoras).
*   **Hồ Sơ Thần Số**: Luận giải sâu về Năm Cá Nhân, Số Thái Độ.

### 5. 🌌 Cung Hoàng Đạo (Zodiac)
*   Tra cứu chi tiết 12 chòm sao phương Tây (Western Zodiac).
*   Thông tin đầy đủ: Nguyên tố, Sao chủ quản, Tính cách, Hợp/Khắc.

### 6. 🛡️ Bảo Mật & An Toàn
*   **Chống Spam**: Rate Limit 20 câu/phút.
*   **An Toàn**: Input validation, ẩn API Keys.
*   **Riêng Tư**: Không lưu data người dùng.

### 7. 📡 Giám Sát & Logging
*   **Google Cloud Logging**: Tích hợp Logs Explorer.
*   **Traceability**: Theo dõi trọn vẹn hành trình (Request -> Agent -> Response) qua `trace_id`.
*   **Dễ Dàng Debug**: Log đầy đủ request body và response detail.

---

## 🛠️ Công Nghệ Sử Dụng

*   **Core AI**: Google Gemini 2.5 Flash (qua `google-genai`).
*   **Framework**: Google Agent Developer Kit (ADK), Flask (Python).
*   **Frontend**: HTML5, CSS3 (Responsive), JavaScript (Vanilla).
*   **Security**: Flask-Limiter, Dotenv.
*   **Charting**: Chart.js (vẽ biểu đồ Radar).
*   **Logging**: Google Cloud Logging (Structured JSON logs).
*   **Search**: DuckDuckGo Search (Enhanced with retry & sources).

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
    ```

4.  **Chạy ứng dụng**:
    ```bash
    python app.py
    ```
    *   Truy cập: `http://localhost:7860`

### Triển khai trên Hugging Face Spaces

1.  **Tạo Space**: Chọn Docker hoặc Global.
2.  **Cấu hình Secrets (Environment Variables)**:
    *   `GOOGLE_API_KEY`: API Key của bạn.
    *   `SESSION_SECRET`: Chuỗi ngẫu nhiên bảo mật session.
    *   `GOOGLE_CREDENTIALS_JSON`: Nội dung file JSON Service Account của Google Cloud (để bật Logging).
3.  **Deploy**: Push code lên Space và tận hưởng!

---



## 📝 Lưu Ý
*   Kết quả chỉ mang tính chất tham khảo và giải trí.
*   "Đức năng thắng số" - Thầy Tư luôn khuyên con cháu sống tốt, làm việc thiện thì vận mệnh tự khắc sẽ hanh thông.

---

**@nconghau25 ❤️  ☕ v1.0.0**
