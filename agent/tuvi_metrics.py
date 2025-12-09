
class TuViMetrics:
    def __init__(self):
        # Dữ liệu cơ bản
        self.ThienCan = ["Canh", "Tân", "Nhâm", "Quý", "Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ"]
        self.DiaChi = ["Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi"]
        self.NguHanh = ["Kim", "Thủy", "Hỏa", "Thổ", "Mộc"] # Mặc định, sẽ tính lại theo Nạp Âm
        
        # Bảng Nạp Âm Ngũ Hành (Rút gọn cho demo, ánh xạ CanChi -> Ngũ Hành)
        # Quy ước: 0=Kim, 1=Thủy, 2=Hỏa, 3=Thổ, 4=Mộc
        self.NapAm = {
            # Giáp Tý/Ất Sửu = Hải Trung Kim (0) - ví dụ
             "Giáp Tý": "Kim", "Ất Sửu": "Kim", "Bính Dần": "Hỏa", "Đinh Mão": "Hỏa",
             "Mậu Thìn": "Mộc", "Kỷ Tỵ": "Mộc", "Canh Ngọ": "Thổ", "Tân Mùi": "Thổ",
             "Nhâm Thân": "Kim", "Quý Dậu": "Kim", "Giáp Tuất": "Hỏa", "Ất Hợi": "Hỏa",
             "Bính Tý": "Thủy", "Đinh Sửu": "Thủy", "Mậu Dần": "Thổ", "Kỷ Mão": "Thổ",
             "Canh Thìn": "Kim", "Tân Tỵ": "Kim", "Nhâm Ngọ": "Mộc", "Quý Mùi": "Mộc",
             "Giáp Thân": "Thủy", "Ất Dậu": "Thủy", "Bính Tuất": "Thổ", "Đinh Hợi": "Thổ",
             "Mậu Tý": "Hỏa", "Kỷ Sửu": "Hỏa", "Canh Dần": "Mộc", "Tân Mão": "Mộc",
             "Nhâm Thìn": "Thủy", "Quý Tỵ": "Thủy", "Giáp Ngọ": "Kim", "Ất Mùi": "Kim",
             "Bính Thân": "Hỏa", "Đinh Dậu": "Hỏa", "Mậu Tuất": "Mộc", "Kỷ Hợi": "Mộc",
             "Canh Tý": "Thổ", "Tân Sửu": "Thổ", "Nhâm Dần": "Kim", "Quý Mão": "Kim",
             "Giáp Thìn": "Hỏa", "Ất Tỵ": "Hỏa", "Bính Ngọ": "Thủy", "Đinh Mùi": "Thủy",
             "Mậu Thân": "Thổ", "Kỷ Dậu": "Thổ", "Canh Tuất": "Kim", "Tân Hợi": "Kim",
             "Nhâm Tý": "Mộc", "Quý Sửu": "Mộc", "Giáp Dần": "Thủy", "Ất Mão": "Thủy",
             "Bính Thìn": "Thổ", "Đinh Tỵ": "Thổ", "Mậu Ngọ": "Hỏa", "Kỷ Mùi": "Hỏa",
             "Canh Thân": "Mộc", "Tân Dậu": "Mộc", "Nhâm Tuất": "Thủy", "Quý Hợi": "Thủy"
        }
        
        # Ngũ hành sinh khắc (Key sinh Value)
        self.Sinh = {"Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"}
        self.Khac = {"Kim": "Mộc", "Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim"}
        
        # Tra cứu Lộc Tồn (Tài Lộc) theo Can
        self.LocTon = {
            "Giáp": "Dần", "Ất": "Mão", "Bính": "Tỵ", "Mậu": "Tỵ",
            "Đinh": "Ngọ", "Kỷ": "Ngọ", "Canh": "Thân", "Tân": "Dậu",
            "Nhâm": "Hợi", "Quý": "Tý"
        }
        
        # Tra cứu Quý Nhân (Phúc Đức) theo Can (Lấy 1 chi đại diện)
        self.QuyNhan = {
            "Giáp": ["Sửu", "Mùi"], "Mậu": ["Sửu", "Mùi"], "Canh": ["Sửu", "Mùi"],
            "Ất": ["Tý", "Thân"], "Kỷ": ["Tý", "Thân"],
            "Bính": ["Hợi", "Dậu"], "Đinh": ["Hợi", "Dậu"],
            "Nhâm": ["Tỵ", "Mão"], "Quý": ["Tỵ", "Mão"],
            "Tân": ["Ngọ", "Dần"]
        }

    def _get_element_can(self, can):
        # Quy ước ngũ hành của Thiên Can
        if can in ["Canh", "Tân"]: return "Kim"
        if can in ["Nhâm", "Quý"]: return "Thủy"
        if can in ["Giáp", "Ất"]: return "Mộc"
        if can in ["Bính", "Đinh"]: return "Hỏa"
        if can in ["Mậu", "Kỷ"]: return "Thổ"
        return "Thổ" 

    def _get_element_chi(self, chi):
        # Quy ước ngũ hành của Địa Chi
        if chi in ["Thân", "Dậu"]: return "Kim"
        if chi in ["Hợi", "Tý"]: return "Thủy"
        if chi in ["Dần", "Mão"]: return "Mộc"
        if chi in ["Tỵ", "Ngọ"]: return "Hỏa"
        if chi in ["Thìn", "Tuất", "Sửu", "Mùi"]: return "Thổ"
        return "Thổ"

    def tinh_chi_so(self, nam_sinh, gioi_tinh="nam"):
        """
        Tính toán chỉ số dựa trên thuật toán Tử Vi cơ bản.
        """
        # 1. Xác định Can Chi
        can = self.ThienCan[nam_sinh % 10]
        chi = self.DiaChi[nam_sinh % 12]
        canchi = f"{can} {chi}"
        
        # 2. Xác định Ngũ Hành Nạp Âm
        menh_nap_am = self.NapAm.get(canchi, "Kim") # Fallback Kim
        
        # 3. Tính điểm THÂN MỆNH (Dựa vào tương quan Can - Chi)
        # Can là Trời, Chi là Đất. 
        # Can khắc Chi (Thiên khắc Địa) -> Vất vả
        # Chi khắc Can (Địa xung Thiên) -> Nghịch lý
        # Can sinh Chi (Thuận lý) -> Tốt
        # Chi sinh Can (Sinh nhập) -> Tốt
        # Tương hòa -> Ổn
        
        el_can = self._get_element_can(can)
        el_chi = self._get_element_chi(chi)
        
        score_than_menh = 70 # Base score
        
        if self.Sinh[el_can] == el_chi: # Can sinh Chi (Thuận)
            score_than_menh += 15 # 85
        elif self.Sinh[el_chi] == el_can: # Chi sinh Can (Được phù trợ)
            score_than_menh += 10 # 80
        elif el_can == el_chi: # Tương hòa
            score_than_menh += 5 # 75
        elif self.Khac[el_can] == el_chi: # Can khắc Chi (Tự lực cánh sinh, vất vả nhưng làm chủ)
            score_than_menh -= 5 # 65
        elif self.Khac[el_chi] == el_can: # Chi khắc Can (Nghịch cảnh)
            score_than_menh -= 10 # 60
            
        # Điều chỉnh theo năm sinh chẵn lẻ (Dương/Âm)
        # Dương Nam/Âm Nữ thì thuận -> cộng điểm
        is_yellow_year = (nam_sinh % 2 == 0) # Năm chẵn là Canh, Nhâm... (Dương) - Check lại: 0=Canh(Dương), 1=Tan(Am) -> Dung
        # Can chi index: 0(Canh-Duong), 1(Tan-Am), ...
        can_index = nam_sinh % 10
        is_yang_can = (can_index % 2 == 0) # 0, 2, 4... là Dương
        
        if (gioi_tinh == "nam" and is_yang_can) or (gioi_tinh != "nam" and not is_yang_can):
            score_than_menh += 5 # Thuận lý Âm Dương
        
        
        # 4. Tính điểm TÀI LỘC (Dựa vào Lộc Tồn và tính chất Can)
        score_tai_loc = 65
        target_loc_ton = self.LocTon.get(can)
        if target_loc_ton == chi:
            score_tai_loc += 25 # Lộc Tồn đóng tại Mệnh (quá ngon) -> 90
        elif self.Sinh[el_chi] == target_loc_ton: # Chi sinh cho Lộc (ví dụ Lộc ở Dần(Mộc), Chi là Hợi(Thủy))
            score_tai_loc += 15
        elif self._get_element_chi(target_loc_ton) == el_chi: # Cùng hành
             score_tai_loc += 10
             
        # Các Can "Giàu": Canh, Tân, Giáp
        if can in ["Canh", "Tân", "Giáp"]:
            score_tai_loc += 5
            
        # 5. Tính điểm PHÚC ĐỨC (Dựa vào Quý Nhân)
        score_phuc_duc = 70
        quynhan_list = self.QuyNhan.get(can, [])
        if chi in quynhan_list:
            score_phuc_duc += 20 # Có Quý Nhân độ mạng -> 90
        
        # Mệnh sinh Cục (hoặc tương đương) - Ở đây dùng Mệnh sinh Chi năm hiện tại (mô phỏng)
        # Giả sử năm nay 2025 (Ất Tỵ - Hỏa)
        # Nếu Mệnh sinh Hỏa -> Tốt cho phúc năm nay
        if self.Sinh.get(menh_nap_am) == "Hỏa":
             score_phuc_duc += 5
             
        # 6. Tính điểm TÌNH DUYÊN (Dựa vào Đào Hoa)
        score_tinh_duyen = 65
        # Tra Đào Hoa (theo Tam Hợp Chi)
        # Thân Tý Thìn -> Dậu
        # Dần Ngọ Tuất -> Mão
        # Tỵ Dậu Sửu -> Ngọ
        # Hợi Mão Mùi -> Tý
        dao_hoa_map = {
            "Thân": "Dậu", "Tý": "Dậu", "Thìn": "Dậu",
            "Dần": "Mão", "Ngọ": "Mão", "Tuất": "Mão",
            "Tỵ": "Ngọ", "Dậu": "Ngọ", "Sửu": "Ngọ",
            "Hợi": "Tý", "Mão": "Tý", "Mùi": "Tý"
        }
        dao_hoa_chi = dao_hoa_map.get(chi)
        
        # Nếu năm sinh trùng Đào Hoa (hiếm, vì Đào Hoa tính theo năm/ngày, xét Chi năm với năm hiện tại?) -> Logic đơn giản:
        # Người có Chi là Tý, Ngọ, Mão, Dậu thường đào hoa hơn (Tứ Chính)
        if chi in ["Tý", "Ngọ", "Mão", "Dậu"]:
            score_tinh_duyen += 10
        elif chi in ["Thìn", "Tuất", "Sửu", "Mùi"]: # Tứ Mộ (Thường cô quả hơn chút)
            score_tinh_duyen -= 5
            
        # Mệnh Thủy/Hỏa thường đa sầu đa cảm -> Tình duyên biến động (cao hoặc thấp)
        if menh_nap_am in ["Thủy", "Hỏa"]:
             score_tinh_duyen += 5
             
        # 7. Tính điểm QUAN LỘC (Sự nghiệp)
        # Dựa vào độ vững của hành Mệnh và quan hệ với năm hiện tại
        score_quan_loc = 60
        # Mệnh Kim/Hỏa thường quyết đoán -> Quan lộc dễ cao
        if menh_nap_am in ["Kim", "Hỏa"]:
            score_quan_loc += 10
        # Can Dương thường hướng ngoại -> Sự nghiệp
        if is_yang_can:
            score_quan_loc += 10
            
        # Normalize scores (max 100, min 40)
        metrics = {
            "than_menh": min(100, max(40, score_than_menh)),
            "tai_loc": min(100, max(40, score_tai_loc)),
            "quan_loc": min(100, max(40, score_quan_loc)),
            "tinh_duyen": min(100, max(40, score_tinh_duyen)),
            "phuc_duc": min(100, max(40, score_phuc_duc))
        }
        
        # Insight
        top_metric = max(metrics, key=metrics.get)
        insight = f"Lá số {can} {chi} ({menh_nap_am}) này nổi bật nhất ở cung {top_metric.replace('_', ' ').title()} ({metrics[top_metric]}/100). "
        
        if metrics['than_menh'] > 80:
             insight += "Thân Mệnh vững vàng, tự chủ cuộc đời tốt."
        elif metrics['phuc_duc'] > 80:
             insight += "Phúc đức dày, gặp hung hóa cát."
        elif metrics['tai_loc'] > 80:
             insight += "Có duyên với tiền bạc, làm ăn dễ phất."
        
        return {
            "metrics": metrics,
            "insight": insight,
            "element": menh_nap_am
        }