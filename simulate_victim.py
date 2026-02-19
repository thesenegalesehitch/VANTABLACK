import requests
import time
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET = "https://localhost:8443"
LOGIN_URL = f"{TARGET}/i/flow/login"
BEACON_URL = f"{TARGET}/__vanta_track"

session = requests.Session()
session.verify = False

def simulate_victim():
    print(f"[*] Victim accessing: {TARGET}")
    try:
        # 1. Landing Page
        resp = session.get(TARGET)
        print(f"[+] Landing Page Status: {resp.status_code}")
        
        # 2. Simulate User Input (Keylogging Beacon)
        print("[*] Simulating keystrokes (user typing credentials)...")
        keystrokes = [
            ("user@example.com", "text"),
            ("P", "password"),
            ("Pa", "password"),
            ("Pas", "password"),
            ("Pass", "password"),
            ("Pass123!", "password")
        ]
        
        for val, field in keystrokes:
            data = {"k": val, "f": field}
            resp = session.post(BEACON_URL, data=data)
            print(f"Beacon Status: {resp.status_code}")
            time.sleep(0.1)
            
        print("[+] Keystrokes sent via Beacon API")

        # 3. Submit Credentials (POST)
        print("[*] Submitting credentials...")
        # Simulating the actual login request structure (simplified)
        login_data = {
            "text": "user@example.com",
            "password": "SuperSecretPassword123!",
            "remember_me": "true"
        }
        resp = session.post(LOGIN_URL, data=login_data)
        print(f"[+] Login POST Status: {resp.status_code}")
        
        if resp.status_code == 200 or resp.status_code == 302:
            print("[+] Credentials submission simulated successfully")
        else:
            print(f"[-] Unexpected login response: {resp.status_code}")

    except Exception as e:
        print(f"[!] Simulation failed: {e}")

if __name__ == "__main__":
    simulate_victim()
