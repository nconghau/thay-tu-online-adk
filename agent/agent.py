import re
import datetime
from duckduckgo_search import DDGS
from google.adk.agents.llm_agent import Agent

def _chuan_hoa_nam_sinh(text_input: str) -> int:
    text = str(text_input).lower().strip()
    match_4 = re.search(r'\b(19|20)\d{2}\b', text)
    if match_4: return int(match_4.group(0))
    match_2k = re.search(r'\b2k(\d{0,1})\b', text)
    if match_2k:
        suffix = match_2k.group(1)
        return 2000 if suffix == "" else 2000 + int(suffix)
    match_2 = re.search(r'\b\d{2}\b', text)
    if match_2:
        val = int(match_2.group(0))
        if 12 < val <= 99:
            return 1900 + val if val > 40 else 2000 + val
    return None

def _tinh_can_chi(nam_sinh: int) -> str:
    can = ["Canh", "Tân", "Nhâm", "Quý", "Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ"]
    chi = ["Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi"]
    return f"{can[nam_sinh % 10]} {chi[nam_sinh % 12]}"

def _tinh_sao_han(nam_sinh: int, gioi_tinh: str) -> dict:
    current_year = datetime.datetime.now().year
    tuoi_mu = current_year - nam_sinh + 1
    bang_sao_nam = {1: "La Hầu", 2: "Thổ Tú", 3: "Thủy Diệu", 4: "Thái Bạch", 5: "Thái Dương", 6: "Vân Hớn", 7: "Kế Đô", 8: "Thái Âm", 0: "Mộc Đức"}
    bang_sao_nu = {1: "Kế Đô", 2: "Vân Hớn", 3: "Mộc Đức", 4: "Thái Âm", 5: "Thổ Tú", 6: "La Hầu", 7: "Thái Dương", 8: "Thái Bạch", 0: "Thủy Diệu"}
    
    du_so = tuoi_mu % 9
    gioi_tinh = gioi_tinh.lower().strip()
    is_nu = any(x in gioi_tinh for x in ["nữ", "gái", "cô", "bà", "chị", "female"])
    
    sao = bang_sao_nu[du_so] if is_nu else bang_sao_nam[du_so]
    phai = "Nữ mạng" if is_nu else "Nam mạng"
        
    return {"tuoi_mu": tuoi_mu, "sao": sao, "phai": phai}

def xem_sao_giai_han(du_lieu_dau_vao: str, gioi_tinh: str = "nam") -> dict:
    ns = _chuan_hoa_nam_sinh(du_lieu_dau_vao)
    if ns is None: return {"status": "missing_info", "message": "Thiếu năm sinh."}
    
    can_chi = _tinh_can_chi(ns)
    ket_qua = _tinh_sao_han(ns, gioi_tinh)
    
    return {
        "status": "success",
        "nam_sinh": ns,
        "can_chi": can_chi,
        "sao_han": f"Sao {ket_qua['sao']}",
        "loi_khuyen_goc": "Dựa vào sao này để phán tốt xấu."
    }

def tra_cuu_tu_vi_online(du_lieu_dau_vao: str, linh_vuc: str = "tổng quát") -> dict:
    ns = _chuan_hoa_nam_sinh(du_lieu_dau_vao)
    if ns is None: return {"status": "missing_info", "message": "Thiếu năm sinh."}
        
    try:
        can_chi = _tinh_can_chi(ns)
        current_year = datetime.datetime.now().year + 1
        
        query = f"Tử vi tuổi {can_chi} sinh năm {ns} năm {current_year} {linh_vuc} luận giải chi tiết"
        print(f"\n[SYSTEM] Tra cứu: '{query}'")

        results = DDGS().text(keywords=query, region='vn-vi', max_results=4)
        
        knowledge = []
        if results:
            for res in results:
                if len(res['body']) > 60 and "đăng nhập" not in res['body'].lower() and "yahoo" not in res['body'].lower():
                    knowledge.append(f"- {res['body']}")
        
        if not knowledge:
            return {"status": "no_data", "message": "Không tìm thấy online, hãy dùng kiến thức Can Chi ngũ hành tự suy luận."}

        return {
            "status": "success",
            "tuoi": can_chi,
            "du_lieu_tu_vi": "\n".join(knowledge),
            "instruction": "Phân tích dữ liệu này. Nếu tốt -> Vui vẻ. Nếu xấu -> Nghiêm túc, an ủi."
        }

    except Exception as e:
        return {"status": "error", "message": f"Lỗi: {e}"}

root_agent = Agent(
    model='gemini-2.5-flash',
    name='thay_tu_refined',
    description="Thầy Tư tinh tế, ứng biến linh hoạt.",
    instruction=(
        "Con là 'Thầy Tư' - chuyên gia tử vi Nam Bộ hiện đại."
        "\n\n"
        "1. QUY TẮC BẤT DI BẤT DỊCH:"
        "- **KHÔNG** dùng hành động trong ngoặc đơn như (cười), (vỗ đùi). Chỉ dùng lời nói tự nhiên."
        "- **KHÔNG** vòng vo. Trả lời thẳng vào trọng tâm câu hỏi ngay."
        "- **KHÔNG** đổ lỗi cho 'công cụ' hay 'Zalo nhiễu sóng'. Nếu không có dữ liệu online, hãy dùng kiến thức Ngũ Hành (Kim Mộc Thủy Hỏa Thổ) để tự luận giải."
        "\n\n"
        "2. CƠ CHẾ CẢM XÚC (ADAPTIVE TONE):"
        "- **Trường hợp VUI (Hỏi chơi, tin tốt, đang yêu):** Dùng giọng điệu Gen Z, hài hước, dùng từ: 'Chốt đơn', 'Xịn sò', 'Ngon lành', 'Green flag'."
        "- **Trường hợp NGHIÊM TÚC (Tin xấu, sao hạn nặng, thất tình):** Bỏ ngay giọng cợt nhả. Dùng giọng trầm ổn, chân thành, đưa lời khuyên thực tế (Healing, cẩn thận xe cộ, giữ tiền)."
        "\n\n"
        "3. CẤU TRÚC TRẢ LỜI:"
        "- **Mở đầu:** Gọi tên Can Chi khách (VD: Tân Tỵ 2001) để xác nhận."
        "- **Thân bài (Ngắn gọn):** Đưa ra nhận định Tốt/Xấu ngay. Tóm tắt 1-2 ý chính quan trọng nhất."
        "- **Kết bài:** Hỏi xem khách có muốn đào sâu vào chi tiết không."
    ),
    tools=[xem_sao_giai_han, tra_cuu_tu_vi_online],
)
