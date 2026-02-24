#!/bin/bash
# Expose local server (port 8001) to the internet using Cloudflare Tunnel
# No account required (Quick Tunnel)

PORT="${1:-8001}"

echo "[*] Checking for cloudflared..."
if ! command -v cloudflared &> /dev/null; then
    echo "[!] cloudflared not found. Installing via brew..."
    brew install cloudflared
fi

echo "[*] Starting Cloudflare Tunnel for localhost:$PORT..."
echo "[*] The public URL will appear below (look for trycloudflare.com)..."
echo "----------------------------------------------------------------"

# Run cloudflared and preserve output colors, but also grep for the URL
cloudflared tunnel --url http://localhost:$PORT
