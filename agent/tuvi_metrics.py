import random

class TuViMetrics:
    def __init__(self):
        # Định nghĩa các trọng số ngũ hành (giả lập data science)
        self.ngu_hanh = ["Kim", "Mộc", "Thủy", "Hỏa", "Thổ"]

    def tinh_chi_so(self, nam_sinh, gioi_tinh):
        """
        Trả về bộ dữ liệu định lượng (0-100) cho các phương diện cuộc sống
        để vẽ biểu đồ Radar.
        """
        # Logic giả lập: Dùng năm sinh làm seed để kết quả luôn cố định với 1 người
        random.seed(nam_sinh)
        
        # 1. Tính toán cơ bản (Mô phỏng thuật toán an sao)
        can_chi_id = nam_sinh % 60
        menh_id = nam_sinh % 5
        
        # 2. Tạo điểm số (Data Science simulation)
        # Aituvi.com thường có: Thân mệnh, Tài chính, Sự nghiệp, Tình cảm, Sức khỏe
        metrics = {
            "than_menh": random.randint(60, 95),  # Thân Mệnh (Sức mạnh nội tại)
            "tai_loc": random.randint(50, 90),    # Tài Bạch (Tiền bạc)
            "quan_loc": random.randint(55, 95),   # Quan Lộc (Sự nghiệp)
            "tinh_duyen": random.randint(40, 85), # Phu Thê (Tình cảm)
            "phuc_duc": random.randint(70, 100)   # Phúc Đức (May mắn)
        }
        
        # 3. Tạo nhận xét ngắn gọn dựa trên điểm số (Insight)
        top_metric = max(metrics, key=metrics.get)
        insight = f"Lá số này có cường điểm ở cung {top_metric.replace('_', ' ').title()} ({metrics[top_metric]}/100)."
        
        return {
            "metrics": metrics,
            "insight": insight,
            "element": self.ngu_hanh[menh_id]
        }