
def luan_giai_than_so_hoc(ngay_sinh_str: str) -> dict:
    """
    Báo cáo Thần số học mini (Số chủ đạo + Năm cá nhân + Số thái độ) theo chuẩn.
    """
    import re
    import datetime
    
    # 1. Parse Digits
    digits = re.findall(r'\d', ngay_sinh_str)
    if not digits or len(digits) < 6:
        return {"status": "error", "message": "Nhập ngày sinh đầy đủ (dd/mm/yyyy) để thầy tính thần số học nghen!"}
    
    # Extract components assuming dd/mm/yyyy or ddmmyyyy flow
    # Simplest safe bet: join all and parse manually if separators exist
    if '/' in ngay_sinh_str:
        parts = ngay_sinh_str.split('/')
        if len(parts) == 3:
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            return {"status": "error", "message": "Định dạng ngày lạ quá."}
    elif '-' in ngay_sinh_str:
        parts = ngay_sinh_str.split('-')
        d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
    else:
        # Fallback for continuous digits like 20111995
        full_str = "".join(digits)
        d = int(full_str[:2])
        m = int(full_str[2:4])
        y = int(full_str[4:])

    def reduce_digit(n, keep_master=False):
        while n > 9:
            if keep_master and n in [11, 22, 33]: break
            n = sum(int(x) for x in str(n))
        return n

    # 2. CALCULATION (Standard)
    
    # Life Path (Cộng tổng rồi rút gọn)
    lp = reduce_digit(sum(int(x) for x in str(d) + str(m) + str(y)), keep_master=True)
    
    # Attitude Number (Ngày + Tháng) -> Ấn tượng ban đầu
    att = reduce_digit(d + m)
    
    # Personal Year (Ngày + Tháng + Năm hiện tại)
    cur_year = datetime.datetime.now().year
    py = reduce_digit(d + m + cur_year)
    
    # 3. INTERPRETATION DATABASE
    py_meanings = {
        1: "Năm của sự khởi đầu mới. Hãy gieo hạt, bắt đầu dự án mới, độc lập tác chiến.",
        2: "Năm của sự cân bằng và kết nối. Hãy hòa giải, tìm đối tác, và lắng nghe trực giác.",
        3: "Năm của sự sáng tạo và niềm vui. Hãy giao lưu, học hỏi kỹ năng mới, tận hưởng cuộc sống.",
        4: "Năm của củng cố và kỷ luật. Hãy xây dựng nền tảng, làm việc chăm chỉ, tổ chức lại cuộc sống.",
        5: "Năm của sự thay đổi và tự do. Hãy đón nhận cơ hội mới, đi du lịch, bứt phá khỏi vùng an toàn.",
        6: "Năm của gia đình và trách nhiệm. Hãy quan tâm người thân, chăm sóc tổ ấm, phụng sự.",
        7: "Năm của chiêm nghiệm và tri thức. Hãy học tập, thiền định, quay vào bên trong để trưởng thành.",
        8: "Năm của thành tựu và quyền lực. Hãy tập trung kinh doanh, tài chính, gặt hái quả ngọt.",
        9: "Năm của buông bỏ và hoàn thiện. Hãy dọn dẹp cái cũ, tha thứ, chuẩn bị cho chu kỳ mới."
    }

    return {
        "status": "success",
        "message": (
            f"📐 **Hồ Sơ Thần Số Học (Pythagoras)**\n"
            f"────────────────────────\n"
            f"🔹 **Số Chủ Đạo: {lp}**\n"
            f"   (Con số định hướng cả cuộc đời bạn)\n\n"
            f"🔹 **Số Thái Độ: {att}**\n"
            f"   (Cách bạn phản ứng với thế giới: {'Quyết liệt' if att in [1,8] else 'Hòa nhã' if att in [2,6,9] else 'Sôi nổi'})\n\n"
            f"🔹 **Năm Cá Nhân {cur_year}: Số {py}**\n"
            f"   💡 *Lời khuyên:* {py_meanings.get(py)}"
        )
    }
