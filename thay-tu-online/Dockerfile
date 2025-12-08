# Sử dụng Python 3.11 Slim (Nhẹ, ổn định, hỗ trợ tốt Google ADK)
FROM python:3.11-slim

# Thiết lập biến môi trường
# PYTHONDONTWRITEBYTECODE: Ngăn python tạo file .pyc (không cần trong docker)
# PYTHONUNBUFFERED: Log in ra console ngay lập tức (dễ debug)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các gói hệ thống cần thiết (curl để healthcheck, build-essential nếu cần compile lib C++)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements trước để tận dụng Docker Cache
COPY requirements.txt .

# Cài đặt dependencies
# --no-cache-dir: Giảm dung lượng image
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Tạo user non-root để chạy app (Best Practice về bảo mật)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose port 8000 (Khớp với app.py)
EXPOSE 8000

# Healthcheck để đảm bảo container đang sống
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Lệnh khởi chạy
CMD ["python", "app.py"]