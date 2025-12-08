from google.adk.agents.llm_agent import Agent
from datetime import datetime
from zoneinfo import ZoneInfo # Thư viện xử lý múi giờ có sẵn trong Python 3.9+

# --- PHẦN 1: ĐỊNH NGHĨA TOOLS (CÔNG CỤ) ---

def get_current_time(timezone: str) -> dict:
    """
    Trả về thời gian hiện tại chính xác theo múi giờ được yêu cầu.
    
    Args:
        timezone (str): Tên múi giờ (ví dụ: 'Asia/Ho_Chi_Minh', 'America/New_York', 'Europe/London').
    """
    try:
        # Lấy giờ thực tế từ hệ thống
        now = datetime.now(ZoneInfo(timezone))
        return {
            "status": "success",
            "timezone": timezone,
            "time": now.strftime("%H:%M:%S"), # Giờ:Phút:Giây
            "date": now.strftime("%Y-%m-%d"), # Năm-Tháng-Ngày
            "day_of_week": now.strftime("%A") # Thứ trong tuần
        }
    except Exception as e:
        # Xử lý nếu AI gửi sai tên múi giờ
        return {
            "status": "error", 
            "message": f"Không tìm thấy múi giờ '{timezone}'. Vui lòng thử lại với tên chuẩn (VD: Asia/Tokyo)."
        }

# --- PHẦN 2: ĐỊNH NGHĨA AGENT ---

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="Trợ lý thời gian quốc tế.",
    instruction=(
        "Bạn là một trợ lý hữu ích chuyên về thời gian. "
        "Khi người dùng hỏi giờ tại một thành phố, hãy suy luận ra 'timezone' của thành phố đó "
        "và sử dụng tool 'get_current_time' để lấy thông tin chính xác. "
        "Trả lời bằng tiếng Việt thân thiện."
    ),
    # Đăng ký tool vào agent tại đây
    tools=[get_current_time],
)

# Dòng này để xác nhận code không lỗi cú pháp khi chạy
if __name__ == "__main__":
    print("Agent 'root_agent' đã sẵn sàng với tool 'get_current_time'.")