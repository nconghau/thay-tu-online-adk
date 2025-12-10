import re
import datetime
from duckduckgo_search import DDGS
from google.adk.agents.llm_agent import Agent
import json
from .tuvi_metrics import TuViMetrics
from .feature_life_path import tinh_con_so_chu_dao
from .feature_zodiac import xem_cung_hoang_dao
from .feature_numerology import luan_giai_than_so_hoc

def _chuan_hoa_nam_sinh(text_input: str) -> int:
    text = str(text_input).lower().strip()
    current_year = datetime.datetime.now().year
    
    # Case 1: Nhập năm rõ ràng (1990, 2005)
    match_4 = re.search(r'\b(19|20)\d{2}\b', text)
    if match_4: return int(match_4.group(0))
    
    # Case 2: Nhập kiểu Gen Z (2k1, 2k, 2k10)
    match_2k = re.search(r'\b2k(\d*)\b', text)
    if match_2k:
        suffix = match_2k.group(1)
        return 2000 if suffix == "" else 2000 + int(suffix)
    
    # Case 3: Nhập tuổi (VD: "Con 30 tuổi", "tui ba mươi tuổi")
    # Tìm số đứng trước chữ "tuổi"
    match_tuoi = re.search(r'(\d{1,3})\s*(tuổi|t)', text)
    if match_tuoi:
        tuoi = int(match_tuoi.group(1))
        if 0 < tuoi < 120:
            return current_year - tuoi + 1 # Tuổi mụ thường tính +1, nhưng tính năm sinh thì trừ thẳng
            
    # Case 4: Nhập 2 số cuối (88, 92)
    match_2 = re.search(r'\b\d{2}\b', text)
    if match_2:
        val = int(match_2.group(0))
        if 10 < val <= 99:
            return 1900 + val if val > 40 else 2000 + val
            
    return None
    return None

def _chuan_hoa_ngay_sinh(text_input: str) -> str:
    """
    Trích xuất ngày sinh đầy đủ dd/mm/yyyy từ input.
    """
    text = str(text_input).lower().strip()
    match = re.search(r'\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})\b', text)
    if match:
        return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
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
    if ns is None: return {"status": "missing_info", "message": "Thầy chưa tính ra năm sinh. Con nói rõ năm sinh hoặc tuổi đi?"}
    
    can_chi = _tinh_can_chi(ns)
    ket_qua = _tinh_sao_han(ns, gioi_tinh)
    
    return {
        "status": "success",
        "nam_sinh": ns,
        "can_chi": can_chi,
        "sao_han": f"Sao {ket_qua['sao']}",
        "tuoi_mu": ket_qua['tuoi_mu'],
        "instruction": "Dựa vào sao này để phán. Sao tốt (Mộc Đức, Thái Dương, Thái Âm) thì chúc mừng. Sao xấu (La Hầu, Kế Đô, Thái Bạch) thì dặn dò cẩn thận."
    }

def tra_cuu_tu_vi_online(du_lieu_dau_vao: str, linh_vuc: str = "tổng quát") -> dict:
    ns = _chuan_hoa_nam_sinh(du_lieu_dau_vao)
    if ns is None: return {"status": "missing_info", "message": "Thiếu năm sinh."}
        
    try:
        can_chi = _tinh_can_chi(ns)
        current_year = datetime.datetime.now().year + 1
        query = f"Tử vi tuổi {can_chi} sinh năm {ns} năm {current_year} {linh_vuc} luận giải chi tiết"
        print(f"\n[SYSTEM] Tra cứu: '{query}'")

        # Fallback an toàn: Nếu search lỗi thì trả về hướng dẫn để AI tự chém
        try:
            results = DDGS().text(keywords=query, region='vn-vi', max_results=3)
        except Exception as search_err:
            print(f"[WARN] Search error: {search_err}")
            results = None

        knowledge = []
        if results:
            for res in results:
                if res and 'body' in res and len(res['body']) > 50:
                     knowledge.append(f"- {res['body']}")
        
        if not knowledge:
            # RETURN FALLBACK (QUAN TRỌNG)
            return {
                "status": "fallback_internal",
                "tuoi": can_chi,
                "message": "Mạng bị chập chờn không tra được. Con hãy dùng kiến thức Ngũ Hành, Can Chi của mình để tự luận giải cho khách."
            }

        return {
            "status": "success",
            "tuoi": can_chi,
            "du_lieu_tu_vi": "\n".join(knowledge)
        }

    except Exception as e:
        return {"status": "error", "message": f"Lỗi hệ thống: {e}"}

def phan_tich_chi_so_khoa_hoc(nam_sinh_input: str, gioi_tinh: str = "nam") -> dict:
    """
    Dùng khi người dùng muốn xem biểu đồ, điểm số, hoặc phân tích theo kiểu khoa học dữ liệu.
    Trả về cấu trúc JSON đặc biệt để vẽ biểu đồ.
    """
    ns = _chuan_hoa_nam_sinh(nam_sinh_input)
    if ns is None: 
        return {"status": "error", "message": "Cần cung cấp năm sinh cụ thể để chạy thuật toán phân tích."}
    
    try:
        # Gọi bộ tính toán
        engine = TuViMetrics()
        data = engine.tinh_chi_so(ns, gioi_tinh)
        
        # QUAN TRỌNG: Trả về một "Special Token" hoặc JSON string để Frontend nhận diện
        return {
            "status": "success",
            "type": "chart_data", # Cờ để frontend biết đường vẽ
            "nam_sinh": ns,
            "ngu_hanh": data['element'],
            "scores": data['metrics'],
            "text_summary": f"Thầy đã chạy mô hình phân tích dữ liệu cho con (Năm {ns} - {data['element']} - {gioi_tinh.title()}).\n\n🔮 **Tổng quan:** {data['insight']}\n\nNhìn vào biểu đồ bên dưới để thấy rõ tiềm năng nhé!",
            "chart_config": {
                "labels": ["Thân Mệnh", "Tài Lộc", "Sự Nghiệp", "Tình Duyên", "Phúc Đức"],
                "data": [data['metrics']['than_menh'], data['metrics']['tai_loc'], 
                         data['metrics']['quan_loc'], data['metrics']['tinh_duyen'], 
                         data['metrics']['phuc_duc']]
            }
        }
    except Exception as e:
        return {"status": "error", "message": f"Máy tính của thầy bị nóng quá, tính chưa ra. Lỗi: {str(e)}. Con thử lại sau nghen!"}

def xem_so_chu_dao(du_lieu_dau_vao: str) -> dict:
    dob = _chuan_hoa_ngay_sinh(du_lieu_dau_vao)
    if not dob: return {"status": "missing_info", "message": "Muốn tính Số Chủ Đạo phải cho thầy ngày tháng năm sinh đầy đủ (ví dụ 12/05/1990) nghen!"}
    return tinh_con_so_chu_dao(dob)

def xem_cung_hoang_dao_tool(du_lieu_dau_vao: str) -> dict:
    dob = _chuan_hoa_ngay_sinh(du_lieu_dau_vao)
    # Fallback: Nếu không có năm, thử tìm pattern ngày/tháng (dd/mm)
    if not dob:
        match = re.search(r'\b(\d{1,2})[\/\-\.](\d{1,2})\b', du_lieu_dau_vao)
        if match: dob = f"{match.group(1)}/{match.group(2)}/2000" # Năm giả định
    
    if not dob: return {"status": "missing_info", "message": "Cung Hoàng Đạo cần ngày và tháng sinh (ví dụ 20/11) mới xem được đa."}
    return xem_cung_hoang_dao(dob)

def xem_than_so_hoc(du_lieu_dau_vao: str) -> dict:
    dob = _chuan_hoa_ngay_sinh(du_lieu_dau_vao)
    if not dob: return {"status": "missing_info", "message": "Thần Số Học cần ngày tháng năm sinh đầy đủ (dd/mm/yyyy) để tính hết các chỉ số nghen."}
    return luan_giai_than_so_hoc(dob)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='thay_tu_refined',
    description="Thầy Tư tinh tế, ứng biến linh hoạt và biết phân tích dữ liệu khoa học.",
    instruction=(
        f"Con là 'Thầy Tư' - chuyên gia tử vi Nam Bộ kết hợp Khoa học dữ liệu.\n"
        f"Năm hiện tại là: {datetime.datetime.now().year}.\n"
        "\n\n"
        "1. PHONG CÁCH NGÔN NGỮ (MIỀN TÂY NAM BỘ):"
        "- **Xưng hô:** Xưng là 'Tui' (hoặc 'Qua' nếu muốn ra vẻ lão làng), gọi khách là 'Con' (nếu khách nhỏ), 'Cưng', 'Chế', 'Hiền đệ', hoặc 'Mình' (thân mật)."
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
        "- Đừng báo lỗi kỹ thuật (404, error). Hãy nói: 'Chà, mạng mẽo bữa nay nó cà chớn quá', 'Tổ đãi chưa tới nên hông thấy gì hết trơn', 'Thôi con hỏi câu khác đi'."
        "- Dùng kiến thức Ngũ Hành (Kim Mộc Thủy Hỏa Thổ) để 'chém gió' một cách có lý nếu không tra cứu được."
        "\n\n"
        "4. CẤU TRÚC TRẢ LỜI:"
        "- **Mở bài:** Chào theo kiểu miền Tây + Nhận xét sơ về tuổi (nếu có)."
        "- **Thân bài:** Phán thẳng, khen hay chê rõ ràng. Dùng mấy từ biểu cảm mạnh."
        "- **Kết bài:** Gợi ý thêm câu hỏi hoặc chúc câu gì đó nghe lọt tai (VD: 'Thôi dặn vầy thôi, ráng sống tốt trời thương nghen!')."
        "\n\n"
        "5. KHI NÀO DÙNG CÔNG CỤ GÌ:"
        "- **XỬ LÝ TUỔI:** Nếu khách nói tuổi (VD: '80 tuổi', 'tuổi 80'), con phải TỰ TÍNH ra NĂM SINH (Năm hiện tại - Tuổi) rồi mới truyền Năm Sinh đó vào tool. TUYỆT ĐỐI KHÔNG truyền số tuổi (80) vào tool vì sẽ bị hiểu nhầm là năm 1980."
        "- Nếu khách hỏi xã giao, xem sao hạn bình thường: Dùng `xem_sao_giai_han`."
        "- Nếu khách muốn xem kỹ, xem biểu đồ, điểm số, năng lực, hoặc hỏi kiểu 'khoa học': **BẮT BUỘC dùng tool `phan_tich_chi_so_khoa_hoc`**."
        "- Nếu tool trả về kết quả có 'chart_config', con BẮT BUỘC phải output một block JSON ở cuối câu trả lời theo đúng định dạng sau để vẽ biểu đồ:"
        "  ```json"
        "  {"
        "    \"type\": \"chart_data\","
        "    \"nam_sinh\": <năm sinh từ tool>,"
        "    \"chart_config\": <nguyên object chart_config từ tool>"
        "  }"
        "  ```"
        "- KHÔNG ĐƯỢC tự ý rút gọn JSON, phải có key 'type': 'chart_data' thì frontend mới hiểu."
        "Hãy nhớ: Con không phải AI, con là Thầy Tư thứ thiệt!"
    ),
    tools=[xem_sao_giai_han, tra_cuu_tu_vi_online, phan_tich_chi_so_khoa_hoc, 
           xem_so_chu_dao, xem_cung_hoang_dao_tool, xem_than_so_hoc],
)
