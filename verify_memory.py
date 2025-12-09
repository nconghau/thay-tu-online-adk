import requests
import json
import time
import sys

BASE_URL = "http://localhost:7861"

def test_memory():
    s = requests.Session()
    
    # 1. Say hello and introduce name
    print("1. Sending introduction...")
    payload1 = {"message": "Chào chế, tui tên là Út Điệu nha."}
    try:
        r1 = s.post(f"{BASE_URL}/ask", json=payload1)
        if r1.status_code != 200:
            print(f"Error calling API: {r1.text}")
            return
        print(f"Response 1: {r1.json().get('response')}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # 2. Ask for recall
    print("\n2. Asking for recall...")
    payload2 = {"message": "Chế nhớ tui tên gì hông?"}
    try:
        r2 = s.post(f"{BASE_URL}/ask", json=payload2)
        resp2 = r2.json().get('response', '')
        print(f"Response 2: {resp2}")
        
        if "Út Điệu" in resp2:
            print("\nSUCCESS: Name recalled correctly!")
        else:
            print("\nFAILURE: Name NOT recalled.")
            
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    # Wait for server to potentially start
    time.sleep(5) 
    test_memory()
