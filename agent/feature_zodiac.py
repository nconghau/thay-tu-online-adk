
def xem_cung_hoang_dao(ngay_sinh_str: str) -> dict:
    """
    Xác định cung hoàng đạo từ ngày sinh (dd/mm/yyyy) với dữ liệu chuẩn chi tiết.
    """
    import re
    
    # 1. Parse Input
    match = re.search(r'(\d{1,2})[\/\-\.](\d{1,2})', ngay_sinh_str)
    if not match:
        return {"status": "error", "message": "Cho thầy xin ngày tháng sinh (ví dụ: 25/12) mới coi cung được nghen."}
        
    day = int(match.group(1))
    month = int(match.group(2))
    
    # 2. Standard Zodiac Database
    # Dữ liệu chuẩn (Standard Western Zodiac)
    zodiac_db = {
        "BachDuong": {
            "name": "Bạch Dương (Aries)", "icon": "♈",
            "range": ((3, 21), (4, 19)),
            "element": "Lửa", "planet": "Sao Hỏa",
            "traits": "Lãnh đạo, dũng cảm, nhiệt huyết, nhưng đôi khi nóng tính và bốc đồng.",
            "match": ["Sư Tử", "Nhân Mã"], "clash": ["Thiên Bình"]
        },
        "KimNguu": {
            "name": "Kim Ngưu (Taurus)", "icon": "♉",
            "range": ((4, 20), (5, 20)),
            "element": "Đất", "planet": "Sao Kim",
            "traits": "Điềm tĩnh, thực tế, kiên định. Thích tiền tài và đồ ăn ngon. Hơi bướng bỉnh.",
            "match": ["Xử Nữ", "Ma Kết"], "clash": ["Bọ Cạp"]
        },
        "SongTu": {
            "name": "Song Tử (Gemini)", "icon": "♊",
            "range": ((5, 21), (6, 21)),
            "element": "Khí", "planet": "Sao Thủy",
            "traits": "Thông minh, linh hoạt, giao tiếp giỏi. Sáng nắng chiều mưa, hay thay đổi.",
            "match": ["Thiên Bình", "Bảo Bình"], "clash": ["Nhân Mã"]
        },
        "CuGiai": {
            "name": "Cự Giải (Cancer)", "icon": "♋",
            "range": ((6, 22), (7, 22)),
            "element": "Nước", "planet": "Mặt Trăng",
            "traits": "Nhạy cảm, sống tình cảm, yêu gia đình. Trực giác tốt nhưng hay suy diễn.",
            "match": ["Bọ Cạp", "Song Ngư"], "clash": ["Ma Kết"]
        },
        "SuTu": {
            "name": "Sư Tử (Leo)", "icon": "♌",
            "range": ((7, 23), (8, 22)),
            "element": "Lửa", "planet": "Mặt Trời",
            "traits": "Tự tin, hào phóng, có tố chất lãnh đạo. Thích được khen ngợi và là trung tâm.",
            "match": ["Bạch Dương", "Nhân Mã"], "clash": ["Bảo Bình"]
        },
        "XuNu": {
            "name": "Xử Nữ (Virgo)", "icon": "♍",
            "range": ((8, 23), (9, 22)),
            "element": "Đất", "planet": "Sao Thủy",
            "traits": "Tỉ mỉ, cầu toàn, phân tích sắc bén. Chăm chỉ nhưng hay soi mói.",
            "match": ["Kim Ngưu", "Ma Kết"], "clash": ["Song Ngư"]
        },
        "ThienBinh": {
            "name": "Thiên Bình (Libra)", "icon": "♎",
            "range": ((9, 23), (10, 23)),
            "element": "Khí", "planet": "Sao Kim",
            "traits": "Thanh lịch, công bằng, yêu cái đẹp. Giỏi ngoại giao nhưng hay do dự.",
            "match": ["Song Tử", "Bảo Bình"], "clash": ["Bạch Dương"]
        },
        "BoCap": {
            "name": "Bọ Cạp (Scorpio)", "icon": "♏",
            "range": ((10, 24), (11, 21)),
            "element": "Nước", "planet": "Sao Diêm Vương",
            "traits": "Bí ẩn, sâu sắc, quyết đoán. Nội tâm phức tạp và hay ghen.",
            "match": ["Cự Giải", "Song Ngư"], "clash": ["Kim Ngưu"]
        },
        "NhanMa": {
            "name": "Nhân Mã (Sagittarius)", "icon": "♐",
            "range": ((11, 22), (12, 21)),
            "element": "Lửa", "planet": "Sao Mộc",
            "traits": "Lạc quan, yêu tự do, thích phiêu lưu. Thẳng thắn đến mức vô tâm.",
            "match": ["Bạch Dương", "Sư Tử"], "clash": ["Song Tử"]
        },
        "MaKet": {
            "name": "Ma Kết (Capricorn)", "icon": "♑",
            "range": ((12, 22), (1, 19)),
            "element": "Đất", "planet": "Sao Thổ",
            "traits": "Nghiêm túc, tham vọng, có trách nhiệm. Thực tế nhưng hơi khô khan.",
            "match": ["Kim Ngưu", "Xử Nữ"], "clash": ["Cự Giải"]
        },
        "BaoBinh": {
            "name": "Bảo Bình (Aquarius)", "icon": "♒",
            "range": ((1, 20), (2, 18)),
            "element": "Khí", "planet": "Sao Thiên Vương",
            "traits": "Sáng tạo, độc lập, tư duy khác biệt. Thân thiện nhưng khó nắm bắt.",
            "match": ["Song Tử", "Thiên Bình"], "clash": ["Sư Tử"]
        },
        "SongNgu": {
            "name": "Song Ngư (Pisces)", "icon": "♓",
            "range": ((2, 19), (3, 20)),
            "element": "Nước", "planet": "Sao Hải Vương",
            "traits": "Mơ mộng, lãng mạn, giàu lòng trắc ẩn. Nhạy cảm nghệ sĩ.",
            "match": ["Cự Giải", "Bọ Cạp"], "clash": ["Xử Nữ"]
        }
    }

    # 3. Find Match
    found_sign = None
    for key, data in zodiac_db.items():
        (start_month, start_day) = data['range'][0]
        (end_month, end_day) = data['range'][1]
        
        # Logic check date range carefully (including year wrap for Capricorn)
        is_match = False
        if start_month == end_month:
            if month == start_month and start_day <= day <= end_day: is_match = True
        elif start_month < end_month:
            if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
                is_match = True
        else: # Wrap around year (Capricorn: Dec to Jan)
            if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
                is_match = True
        
        if is_match:
            found_sign = data
            break
            
    if not found_sign:
        return {"status": "error", "message": "Ngày sinh này lạ quá, thầy tìm không ra chòm sao."}

    # 4. Format Output
    msg = (
        f"🌟 **Cung Hoàng Đạo**: {found_sign['icon']} **{found_sign['name']}**\n"
        f"- **Nguyên tố**: {found_sign['element']} | **Sao chiếu mệnh**: {found_sign['planet']}\n"
        f"- **Tính cách**: {found_sign['traits']}\n"
        f"- **Hợp**: {', '.join(found_sign['match'])} | **Khắc**: {', '.join(found_sign['clash'])}"
    )

    return {
        "status": "success",
        "zodiac": found_sign['name'],
        "message": msg
    }
