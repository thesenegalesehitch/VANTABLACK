import requests
import json
import time
import os

SERVER_URL = "http://127.0.0.1:8080/login"
CAPTURE_FILE = "captures.json"

def test_login_capture():
    # Ensure server is running (we assume it is or will be)
    print(f"[*] Testing capture on {SERVER_URL}")
    
    payload = {
        "username": "test_user_verify",
        "password": "test_password_verify"
    }
    
    try:
        # Send login request with User-Agent
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        r = requests.post(SERVER_URL, json=payload, headers=headers, timeout=5)
        print(f"[*] Response: {r.status_code} {r.text}")
        
        if r.status_code != 200:
            print("[!] Login request failed")
            return False
            
        # Check capture file
        time.sleep(1) # Wait for background task
        if not os.path.exists(CAPTURE_FILE):
            print(f"[!] Capture file {CAPTURE_FILE} not found")
            return False
            
        with open(CAPTURE_FILE, "r") as f:
            captures = json.load(f)
            
        # Look for our entry
        found = False
        for c in captures:
            data = c.get("data", {})
            if data.get("username") == "test_user_verify" and data.get("password") == "test_password_verify":
                found = True
                print("[+] Capture verified successfully!")
                break
        
        if not found:
            print("[!] Capture entry not found in file")
            return False
            
        return True
        
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

if __name__ == "__main__":
    if test_login_capture():
        exit(0)
    else:
        exit(1)
