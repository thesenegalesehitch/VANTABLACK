import asyncio
import sys
import os
import aiohttp
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Add current directory to path
sys.path.append(os.getcwd())

from core.net.tunnel import TunnelManager

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Infrastructure Check OK - Vantablack Tunnel Test")

def start_server(port):
    httpd = HTTPServer(('localhost', port), SimpleHandler)
    httpd.serve_forever()

async def test_tunnel(provider, port):
    print(f"\nTesting {provider} tunnel on port {port}...")
    tunnel = TunnelManager(port, provider)
    
    try:
        url = await tunnel.start()
        print(f"Tunnel URL obtained: {url}")
        
        if "http" not in url:
            print("FAILED: Invalid URL format")
            return
            
        print("Waiting 5 seconds for DNS propagation...")
        await asyncio.sleep(5)

        # Verify connectivity
        print("Verifying connectivity...")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        if "Infrastructure Check OK" in text:
                            print(f"SUCCESS: {provider} tunnel is working and reachable!")
                        else:
                            print(f"WARNING: Reachable but content mismatch. Got: {text[:50]}...")
                    else:
                        print(f"FAILED: HTTP {resp.status}")
            except Exception as e:
                print(f"FAILED: Connectivity check error: {e}")
                
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        print(f"Stopping {provider} tunnel...")
        await tunnel.stop()

async def main():
    port = 8085
    
    # Start local server in a thread
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    print(f"Local server started on port {port}")
    
    # Give server a moment to start
    await asyncio.sleep(1)
    
    # Test Cloudflare
    await test_tunnel("cloudflared", port)
    
    # Test Ngrok
    await test_tunnel("ngrok", port)

if __name__ == "__main__":
    asyncio.run(main())
