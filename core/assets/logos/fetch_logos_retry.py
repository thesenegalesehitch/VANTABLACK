#!/usr/bin/env python3
import requests
import os
import time

LOGOS = {
    "google": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/500px-Google_2015_logo.svg.png",
    "microsoft": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/500px-Microsoft_logo.svg.png",
    "instagram": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/500px-Instagram_logo_2016.svg.png",
    "facebook": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Facebook_f_logo_%282019%29.svg/500px-Facebook_f_logo_%282019%29.svg.png",
    "linkedin": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/LinkedIn_logo_initials.png/500px-LinkedIn_logo_initials.png",
    "amazon": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Amazon_logo.svg/500px-Amazon_logo.svg.png",
    "apple": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/500px-Apple_logo_black.svg.png",
    "discord": "https://upload.wikimedia.org/wikipedia/en/thumb/9/98/Discord_logo.svg/500px-Discord_logo.svg.png",
    "dropbox": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Dropbox_Icon.svg/500px-Dropbox_Icon.svg.png",
    "github": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/GitHub_Invertocat_Logo.svg/500px-GitHub_Invertocat_Logo.svg.png",
    "paypal": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/PayPal.svg/500px-PayPal.svg.png",
    "reddit": "https://upload.wikimedia.org/wikipedia/en/thumb/b/bd/Reddit_Logo_Icon.svg/500px-Reddit_Logo_Icon.svg.png",
    "slack": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Slack_icon_2019.svg/500px-Slack_icon_2019.svg.png",
    "tiktok": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a9/TikTok_logo.svg/500px-TikTok_logo.svg.png",
    "yahoo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Yahoo%21_%282019%29.svg/500px-Yahoo%21_%282019%29.svg.png",
}

def download_logos():
    print("Downloading Red Team Assets (Logos)...")
    if not os.path.exists("core/assets/logos"):
        os.makedirs("core/assets/logos")
        
    for name, url in LOGOS.items():
        path = f"core/assets/logos/{name}.png"
        if os.path.exists(path):
            print(f"[SKIP] {name} already exists")
            continue
            
        try:
            print(f"Downloading {name}...")
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
                print(f"[OK] {name}")
            else:
                print(f"[FAIL] {name}: HTTP {r.status_code}")
            
            time.sleep(2) # Be polite
        except Exception as e:
            print(f"[ERROR] {name}: {e}")

if __name__ == "__main__":
    download_logos()
