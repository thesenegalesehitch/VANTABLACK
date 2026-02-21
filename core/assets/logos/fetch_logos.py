#!/usr/bin/env python3
import requests
import os

LOGOS = {
    "twitter": "https://upload.wikimedia.org/wikipedia/commons/5/5a/X_icon_2.svg",
    "google": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
    "microsoft": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
    "linkedin": "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png",
    "facebook": "https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg",
}

def download_logos():
    print("Downloading Red Team Assets (Logos)...")
    for name, url in LOGOS.items():
        ext = url.split(".")[-1]
        path = f"core/assets/logos/{name}.{ext}"
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
                print(f"[OK] {name}")
            else:
                print(f"[FAIL] {name}: HTTP {r.status_code}")
        except Exception as e:
            print(f"[ERROR] {name}: {e}")

if __name__ == "__main__":
    download_logos()
