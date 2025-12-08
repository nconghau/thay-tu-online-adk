#!/bin/bash

# Tên file đầu ra
OUTPUT_FILE="FULL_PROJECT_CODE.txt"

# Xóa file cũ nếu tồn tại
if [ -f "$OUTPUT_FILE" ]; then
    rm "$OUTPUT_FILE"
fi

echo "--- ĐANG XUẤT CODE PYTHON RA FILE $OUTPUT_FILE ---"

# 1. Ghi cây thư mục vào đầu file (để dễ hình dung cấu trúc)
# Kiểm tra nếu có lệnh 'tree' thì dùng, không thì bỏ qua
echo "================================================================================" >> "$OUTPUT_FILE"
echo "CẤU TRÚC THƯ MỤC DỰ ÁN" >> "$OUTPUT_FILE"
echo "================================================================================" >> "$OUTPUT_FILE"

if command -v tree &> /dev/null; then
    # Loại bỏ venv, git, cache khi in cây thư mục
    tree -I "venv|env|.git|__pycache__|.idea|.vscode|*.egg-info|build|dist" >> "$OUTPUT_FILE"
else
    # Fallback nếu không có lệnh tree: dùng find để liệt kê
    find . -maxdepth 3 -not -path '*/.*' -not -path './venv*' -not -path './__pycache__*' >> "$OUTPUT_FILE"
fi

echo -e "\n\n" >> "$OUTPUT_FILE"

# 2. Tìm và xuất nội dung từng file
# - Loại bỏ thư mục: venv, .git, __pycache__, .idea, .vscode, build, dist
# - Chỉ lấy file đuôi: .py, Dockerfile, requirements.txt, .env.example (quan trọng cho deploy)

find . -type f \( -name "*.py" -o -name "Dockerfile" -o -name "requirements.txt" -o -name "app.py" \) \
    -not -path "*/venv/*" \
    -not -path "*/env/*" \
    -not -path "*/.git/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.idea/*" \
    -not -path "*/.vscode/*" \
    -not -path "*/site-packages/*" \
    | while read -r file; do
        
        echo "Đang xử lý: $file"
        
        # Kẻ đường phân cách và ghi tên file
        echo "================================================================================" >> "$OUTPUT_FILE"
        echo "FILE START: $file" >> "$OUTPUT_FILE"
        echo "================================================================================" >> "$OUTPUT_FILE"
        
        # Ghi nội dung file vào
        cat "$file" >> "$OUTPUT_FILE"
        
        # Xuống dòng và kết thúc file
        echo -e "\n" >> "$OUTPUT_FILE"
        echo "FILE END: $file" >> "$OUTPUT_FILE"
        echo -e "\n\n" >> "$OUTPUT_FILE"
done

echo "--- HOÀN TẤT! KIỂM TRA FILE: $OUTPUT_FILE ---"