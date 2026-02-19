"""
Behavior Logger Plugin
======================
Logs user behavior (mouse movements, clicks, keystrokes) to a file.
Useful for Red Team analysis of user interaction with the phishing page.
"""

import logging
import json
import os
from datetime import datetime
from plugins.plugin_api import Plugin, HookType, HookContext

logger = logging.getLogger("plugin.behavior_logger")

class BehaviorLoggerPlugin(Plugin):
    name = "BehaviorLogger"
    version = "1.0.0"
    author = "Vanta Red Team"
    description = "Logs user interactions to disk"

    def __init__(self):
        self.log_dir = "logs/behavior"
        os.makedirs(self.log_dir, exist_ok=True)

    def register_hooks(self, register_callback):
        # We hook into 'http.request.intercept' to catch POSTs to /behavior/log endpoint
        # Or we can use a custom hook if the interceptor emits one.
        # For now, let's assume we catch generic requests and filter.
        register_callback(HookType.HTTP_REQUEST_INTERCEPT, self.on_request)

    async def on_request(self, context: HookContext):
        flow = context.flow
        if flow.request.path.endswith("/behavior/log") and flow.request.method == "POST":
            try:
                data = json.loads(flow.request.content)
                session_id = data.get("session_id", "unknown")
                timestamp = datetime.now().isoformat()
                
                log_file = os.path.join(self.log_dir, f"session_{session_id}.jsonl")
                
                entry = {
                    "timestamp": timestamp,
                    "event": data.get("event"),
                    "details": data.get("details"),
                    "ip": flow.client_conn.address[0]
                }
                
                with open(log_file, "a") as f:
                    f.write(json.dumps(entry) + "\n")
                
                logger.info(f"Logged behavior for session {session_id}")
                
            except Exception as e:
                logger.error(f"Failed to log behavior: {e}")
