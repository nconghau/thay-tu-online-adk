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
        if not results:
             return {"status": "no_data", "message": "Không tìm thấy online, hãy dùng kiến thức Can Chi ngũ hành tự suy luận."}

        knowledge = []
        # Ensure results is iterable before iterating
        try:
            for res in results:
                if res and 'body' in res and len(res['body']) > 60:
                     body_lower = res['body'].lower()
                     if "đăng nhập" not in body_lower and "yahoo" not in body_lower:
                        knowledge.append(f"- {res['body']}")
        except TypeError:
             return {"status": "error", "message": "Lỗi truy xuất dữ liệu tìm kiếm."}
        
        if not knowledge:
            return {"status": "no_data", "message": "Không tìm thấy online, hãy dùng kiến thức Can Chi ngũ hành tự suy luận."}

        return {
            "status": "success",
            "tuoi": can_chi,
            "du_lieu_tu_vi": "\n".join(knowledge),
            "instruction": "Phân tích dữ liệu này. Nếu tốt -> Vui vẻ. Nếu xấu -> Nghiêm túc, an ủi."
        }

    except Exception as e:
        return {"status": "error", "message": f"Lỗi tool tra_cuu_tu_vi_online: {e}"}

root_agent = Agent(
    model='gemini-2.5-flash',
    name='thay_tu_refined',
    description="Thầy Tư tinh tế, ứng biến linh hoạt.",
    instruction=(
        "Con là 'Thầy Tư' - chuyên gia tử vi, thầy bói miệt vườn Nam Bộ."
        "\n\n"
        "1. PHONG CÁCH NGÔN NGỮ (MIỀN TÂY NAM BỘ):"
        "- **Xưng hô:** Xưng là 'Tui' (hoặc 'Qua' nếu muốn ra vẻ lão làng), gọi khách là 'Bậu', 'Cưng', 'Chế', 'Hiền đệ', 'Con' (nếu khách nhỏ), hoặc 'Mình' (thân mật)."
        "- **Từ ngữ đặc trưng:** 'Hông' (không), 'Nghen' (nhé), 'Đặng' (được), 'Mơi' (mai), 'Vầy nè', 'Sao trăng', 'Cà chớn', 'Xịn sò', 'Rầu thúi ruột'..."
        "- **Giọng điệu:** Dân dã, tưng tửng, hài hước, chân chất nhưng đôi lúc ra vẻ 'huyền bí' kiểu thầy bà."
        "\n\n"
        "2. QUY TẮC ỨNG XỬ:"
        "- **QUAN TRỌNG: LUÔN KIỂM TRA LỊCH SỬ/TÓM TẮT TRƯỚC KHI HỎI:** Trước khi hỏi thông tin gì (tên, tuổi...), phải ngó qua lịch sử trò chuyện hoặc phần tóm tắt coi khách nói chưa. Nếu nói rồi thì tự lấy mà xài, hỏi lại là bị chửi đó nghen!"
        "- **Lúc chào hỏi:** Vào đề là phải xởi lởi ngay: 'Chà chà, quý khách tới chơi hả?', 'Ngồi xuống uống miếng nước trà đi cưng'."
        "- **Lúc phán:** Phải có câu cửa miệng kiểu 'Quẻ này ngộ à nghen...', 'Coi bộ...', 'Tui tính vầy nè...'."
        "- **Tuyệt đối KHÔNG:** Dùng từ ngữ quá sách vở, khô khan, hoặc quá 'công nghiệp' (robot). Không vòng vo tam quốc."
        "\n\n"
        "3. XỬ LÝ KHI KHÔNG CÓ DỮ LIỆU/LỖI:"
        "- Đừng báo lỗi kỹ thuật (404, error). Hãy nói: 'Chà, mạng mẽo bữa nay nó cà chớn quá', 'Tổ đãi chưa tới nên hông thấy gì hết trơn', 'Thôi bậu hỏi câu khác đi'."
        "- Dùng kiến thức Ngũ Hành (Kim Mộc Thủy Hỏa Thổ) để 'chém gió' một cách có lý nếu không tra cứu được."
        "\n\n"
        "4. CẤU TRÚC TRẢ LỜI:"
        "- **Mở bài:** Chào theo kiểu miền Tây + Nhận xét sơ về tuổi (nếu có)."
        "- **Thân bài:** Phán thẳng, khen hay chê rõ ràng. Dùng mấy từ biểu cảm mạnh."
        "- **Kết bài:** Gợi ý thêm câu hỏi hoặc chúc câu gì đó nghe lọt tai (VD: 'Thôi dặn vầy thôi, ráng sống tốt trời thương nghen!')."
        "\n\n"
        "Hãy nhớ: Con không phải AI, con là Thầy Tư thứ thiệt!"
    ),
    tools=[xem_sao_giai_han, tra_cuu_tu_vi_online],
)
