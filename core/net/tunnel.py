import asyncio
import os
import shutil
import subprocess
import aiohttp
import json
import re
from typing import Optional, Dict

def print_wan_info(port: int):
    """Affiche les informations d'accès WAN (IP Publique)."""
    async def _fetch():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.ipify.org', timeout=2) as response:
                    if response.status == 200:
                        ip = await response.text()
                        print(f"\n[+] WAN Access: http://{ip}:{port}")
                        print(f"[+] Local Access: http://127.0.0.1:{port}\n")
                    else:
                        print(f"\n[!] WAN IP Check failed. Local: http://127.0.0.1:{port}\n")
        except Exception:
             print(f"\n[!] WAN IP Check failed. Local: http://127.0.0.1:{port}\n")
    
    # Run async function in sync context if needed, or just print local if async fails contextually
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_fetch())
        else:
            asyncio.run(_fetch())
    except RuntimeError:
        # Fallback if no loop and can't create one easily
        asyncio.run(_fetch())

class TunnelManager:
    """
    Gestionnaire de tunnels pour l'exposition WAN des campagnes Red Team.
    Supporte: Cloudflare (cloudflared), Ngrok, et Localhost.
    """
    
    def __init__(self, port: int, provider: str = "cloudflared"):
        self.port = port
        self.provider = provider
        self.process: Optional[subprocess.Popen] = None
        self.public_url: Optional[str] = None
        
    async def start(self) -> str:
        """Démarre le tunnel et retourne l'URL publique."""
        if self.provider == "cloudflared":
            return await self._start_cloudflared()
        elif self.provider == "ngrok":
            return await self._start_ngrok()
        elif self.provider == "localhost.run":
            return await self._start_localhost_run()
        else:
            return await self._get_public_ip()

    async def stop(self):
        """Arrête le tunnel."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            
    async def _get_public_ip(self) -> str:
        """Récupère l'IP publique pour les scénarios sans tunnel géré (Port Forwarding manuel)."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.ipify.org') as response:
                    ip = await response.text()
                    return f"http://{ip}:{self.port}"
        except Exception:
            return f"http://0.0.0.0:{self.port}"

    async def _start_cloudflared(self) -> str:
        """Lance un tunnel Cloudflare Quick (TryCloudflare)."""
        if not shutil.which("cloudflared"):
            # Try to find in common paths or prompt
            print("[!] cloudflared non trouvé. Installation recommandée pour le support WAN.")
            print("    brew install cloudflared")
            return await self._get_public_ip()
            
        cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{self.port}"]
        
        # Démarrage asynchrone du processus
        self.process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        
        # Attente et extraction de l'URL
        # Cloudflared outputs to stderr
        print("[*] Starting cloudflared tunnel...")
        # We need to read line by line from stderr until we find the URL
        # Since Popen is blocking for readline, we use a loop with small sleeps and non-blocking read attempts if possible
        # Or just use pexpect if available, but let's stick to standard lib + simple logic
        
        # Note: Implementing robust non-blocking read from stderr in Python without threads/asyncio subprocess is tricky
        # Let's try to read lines for a few seconds.
        
        import time
        max_retries = 20
        url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
        
        # Since we can't easily read stderr non-blocking without fcntl (unix only), let's use a simple approach:
        # We assume cloudflared outputs the URL quickly.
        # But `process.stderr` is a file object.
        
        # BETTER APPROACH: Use a thread to read stderr and put lines in a queue
        import threading
        import queue
        q = queue.Queue()
        
        def reader(pipe, out_queue):
            try:
                for line in iter(pipe.readline, ''):
                    out_queue.put(line)
            except Exception:
                pass
            finally:
                pipe.close()

        t = threading.Thread(target=reader, args=(self.process.stderr, q))
        t.daemon = True
        t.start()
        
        found_url = None
        for _ in range(30): # 15 seconds max
            try:
                line = q.get_nowait()
                # print(f"DEBUG: {line.strip()}") # Uncomment for debug
                match = url_pattern.search(line)
                if match:
                    found_url = match.group(0)
                    break
            except queue.Empty:
                if self.process.poll() is not None:
                    break
                await asyncio.sleep(0.5)
        
        if found_url:
            return found_url
        else:
            return "Error: Could not retrieve Cloudflare URL (Check logs or install cloudflared)"

    async def _start_ngrok(self) -> str:
        """Lance un tunnel Ngrok."""
        if not shutil.which("ngrok"):
             print("[!] ngrok non trouvé. Installation recommandée: brew install ngrok/ngrok/ngrok")
             return await self._get_public_ip()
             
        # Commande simplifiée
        cmd = ["ngrok", "http", str(self.port)]
        self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Attente que l'API locale ngrok soit dispo
        for _ in range(10):
            await asyncio.sleep(1)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('http://127.0.0.1:4040/api/tunnels') as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data['tunnels']:
                                return data['tunnels'][0]['public_url']
            except Exception:
                pass
                
        return "Error retrieving Ngrok URL (Ensure ngrok is authenticated)"

    async def _start_localhost_run(self) -> str:
        """Lance un tunnel via localhost.run (SSH). Pas de binaire requis, juste SSH."""
        # ssh -R 80:localhost:8080 nokey@localhost.run
        cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{self.port}", "nokey@localhost.run"]
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Localhost.run outputs URL to stdout
        import threading
        import queue
        q = queue.Queue()
        
        def reader(pipe, out_queue):
            try:
                for line in iter(pipe.readline, ''):
                    out_queue.put(line)
            except Exception:
                pass
            finally:
                pipe.close()

        t = threading.Thread(target=reader, args=(self.process.stdout, q))
        t.daemon = True
        t.start()
        
        found_url = None
        for _ in range(20):
            try:
                line = q.get_nowait()
                if "domain" in line or ".lhr.life" in line or ".localhost.run" in line:
                    # Extract URL usually at the end or explicitly stated
                    # Example output: "Connect to http://nephew-tuna.localhost.run or https://nephew-tuna.localhost.run"
                    match = re.search(r"https?://[a-zA-Z0-9-]+\.(?:lhr\.life|localhost\.run)", line)
                    if match:
                        found_url = match.group(0)
                        break
            except queue.Empty:
                if self.process.poll() is not None:
                    break
                await asyncio.sleep(0.5)
                
        if found_url:
            return found_url
        else:
            return "Error starting localhost.run tunnel"
