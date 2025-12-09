import requests
import json
import time

BASE_URL = "http://localhost:7863"

def test_optimization():
    print("Starting optimization test...")
    s = requests.Session()
    
    # 1. Provide User Info
    print("\n1. Providing User Info...")
    payload1 = {"message": "Chào thầy, tui là Hai Lúa, năm nay 60 tuổi, mệnh Kim."}
    try:
        r1 = s.post(f"{BASE_URL}/ask", json=payload1)
        print(f"Response 1: {r1.json().get('response')}")
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. Chat to fill context (Simulate long conversation)
    print("\n2. Filling context with chit-chat...")
    messages = [
        "Hôm nay trời đẹp không thầy?",
        "Tui muốn trồng cây xoài trước nhà được hông?",
        "Con trai tui nó mới cưới vợ.",
        "Bữa nay tui ăn cơm tấm sườn bì chả ngon lắm.",
        "Thầy biết hát vọng cổ hông?",
        "Chuyện xóm tui vui lắm để tui kể thầy nghe...",
        "Có con chó nhà hàng xóm nó sủa tối ngày.",
        "Thầy coi giùm tui ngày mai tốt ngày hông?",
        "Tui tính đi Sài Gòn chơi một chuyến."
    ]
    
    for i, msg in enumerate(messages):
        try:
            r = s.post(f"{BASE_URL}/ask", json={"message": msg})
           # print(f"Turn {i+1}: {r.json().get('response')[:50]}...")
        except:
             pass
    print("Produced 9 turns of chit-chat to trigger potential summarization/filling.")

    # 3. Ask Question requiring early context
    print("\n3. Asking question requiring memory of name and age...")
    payload_check = {"message": "Nãy giờ nói nhiều quá, thầy quên tui là ai chưa? Tui bao nhiêu tuổi?"}
    try:
        r_check = s.post(f"{BASE_URL}/ask", json=payload_check)
        response = r_check.json().get('response', '')
        print(f"Final Response: {response}")
        
        if "Hai Lúa" in response and "60" in response:
            print("\nSUCCESS: Agent remembered Name and Age despite chatter.")
        else:
            print("\nFAILURE: Agent forgot details.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    time.sleep(5)
    test_optimization()
