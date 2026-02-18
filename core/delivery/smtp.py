"""
Vantablack Core v5 - SMTP Connector
===================================

Handles:
- Async SMTP Delivery
- Connection pooling/rotation
- TLS encryption
"""

import asyncio
import logging
import smtplib
from typing import List, Dict, Optional
from email.message import EmailMessage
from email.headerregistry import Address
from aiosmtplib import SMTP
from pydantic import BaseModel, Field

class SMTPConfig(BaseModel):
    host: str
    port: int = 587
    username: str
    password: str
    use_tls: bool = True
    from_name: str
    from_email: str
    reply_to: Optional[str] = None
    timeout: int = 30

class SMTPClient:
    def __init__(self, config: SMTPConfig):
        self.config = config
        self.logger = logging.getLogger(f"vantablack.delivery.smtp.{config.host}")
        
    async def send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """
        Send a single email asynchronously.
        """
        message = EmailMessage()
        message["From"] = f"{self.config.from_name} <{self.config.from_email}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        if self.config.reply_to:
            message["Reply-To"] = self.config.reply_to

        # Add plain text version
        message.set_content(text_body)
        # Add HTML version
        message.add_alternative(html_body, subtype="html")

        try:
            client = SMTP(
                hostname=self.config.host, 
                port=self.config.port,
                use_tls=self.config.use_tls,
                timeout=self.config.timeout
            )
            
            async with client:
                await client.login(self.config.username, self.config.password)
                await client.send_message(message)
                
            self.logger.info(f"Sent email to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

class SMTPRotator:
    """
    Manages multiple SMTP clients and rotates between them.
    """
    def __init__(self, configs: List[SMTPConfig]):
        self.clients = [SMTPClient(cfg) for cfg in configs]
        self._index = 0
        self._lock = asyncio.Lock()

    async def get_next_client(self) -> SMTPClient:
        async with self._lock:
            client = self.clients[self._index]
            self._index = (self._index + 1) % len(self.clients)
            return client
