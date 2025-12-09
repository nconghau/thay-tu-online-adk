
def tinh_con_so_chu_dao(ngay_sinh_str: str) -> dict:
    """
    Tính số chủ đạo (Life Path Number) theo chuẩn Pythagoras.
    """
    import re
    digits = re.findall(r'\d', ngay_sinh_str)
    if not digits or len(digits) < 6:
        return {"status": "error", "message": "Cần ngày tháng năm sinh đầy đủ (ví dụ: 12/05/1990) mới tính chuẩn nghen!"}
    
    # Tính tổng theo phương pháp cộng dọc (Vertical) hoặc cộng ngang (Horizontal)
    # Chuẩn phổ biến hiện nay: Cộng tổng từng thành phần (Ngày + Tháng + Năm) sau đó rút gọn
    # VD: 20/11/1995 -> 20 + 11 + 1995 -> 2+0 + 1+1 + 1+9+9+5 = 2 + 2 + 24(6) = 10 -> 1
    # Nhưng cách đơn giản nhất là cộng tuốt luốt các số rồi rút gọn.
    
    total = sum(int(d) for d in digits)
    
    def reduce_sum(n):
        while n > 9 and n not in [11, 22, 33]: # Giữ lại số Master
            n = sum(int(d) for d in str(n))
        return n
        
    so_chu_dao = reduce_sum(total)
    
    # Dữ liệu chuẩn Pythagoras (Ngắn gọn)
    descriptions = {
        1: "Số 1 (Leader): Độc lập, tiên phong, quyết đoán. Bạn sinh ra để dẫn đầu và tự đứng trên đôi chân mình.",
        2: "Số 2 (Peacemaker): Nhạy cảm, hòa giải, trực giác tốt. Bạn là chất keo kết nối mọi người.",
        3: "Số 3 (Communicator): Sáng tạo, vui vẻ, hoạt ngôn. Bạn mang niềm vui và cảm hứng đến thế giới.",
        4: "Số 4 (Builder): Thực tế, kỷ luật, tỉ mỉ. Bạn là nền móng vững chắc cho mọi thành công.",
        5: "Số 5 (Adventurer): Tự do, linh hoạt, thích trải nghiệm. Bạn ghét sự ràng buộc và tẻ nhạt.",
        6: "Số 6 (Nurturer): Trách nhiệm, yêu thương, chăm sóc. Gia đình là số một với bạn.",
        7: "Số 7 (Seeker): Tri thức, chiêm nghiệm, bí ẩn. Bạn thích tìm hiểu bản chất của vạn vật.",
        8: "Số 8 (Executive): Tài chính, quyền lực, điều hành. Bạn có duyên với tiền bạc và kinh doanh.",
        9: "Số 9 (Humanitarian): Cho đi, bao dung, vị tha. Bạn có tấm lòng nhân ái vì cộng đồng.",
        10: "Số 10 (Leader - Biến thể của 1): Tự tin, mạnh mẽ, dễ thích nghi. (Giống số 1 nhưng mềm mỏng hơn).",
        11: "Số 11 (Master Intuitive): Trực giác tâm linh cực mạnh, nhạy bén. Người truyền cảm hứng tinh thần.",
        22: "Số 22 (Master Builder): Tầm nhìn vĩ mô, biến giấc mơ lớn thành hiện thực. Số của kiến trúc sư đại tài.",
        33: "Số 33 (Master Teacher): Chữa lành, hướng dẫn, tình yêu đại đồng. Số của bậc thầy tâm linh."
    }
    
    # Map 1 -> 10 nếu theo trường phái VN hay dùng số 10 thay cho 1
    description = descriptions.get(so_chu_dao)
    if not description and so_chu_dao == 10: # Fallback just in case
        description = descriptions[1]

    return {
        "status": "success",
        "so_chu_dao": so_chu_dao,
        "message": f"🔢 **Số Chủ Đạo (Life Path)**: Số **{so_chu_dao}**\n\n👉 {description}"
    }
