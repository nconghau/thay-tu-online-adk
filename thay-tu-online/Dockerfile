# Sử dụng Python 3.11 Slim
FROM python:3.11-slim

# Setup biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Tạo user có ID 1000 (Yêu cầu của Hugging Face để tránh lỗi Permission)
RUN useradd -m -u 1000 user
WORKDIR /app

# Cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code và cấp quyền cho user 1000
COPY --chown=user . /app

# Chuyển sang user non-root
USER user

# Mở port 7860 (BẮT BUỘC TRÊN HUGGING FACE)
EXPOSE 7860

# Dùng Gunicorn để chạy App. 
# -b 0.0.0.0:7860: Bind vào port 7860
# app:app : Tìm biến 'app' trong file 'app.py'
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]