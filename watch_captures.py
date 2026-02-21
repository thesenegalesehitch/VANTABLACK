import time
import json
import os
from rich.console import Console
from rich.panel import Panel

console = Console()
CAPTURE_FILE = "captures.json"

console.print("[bold green]Monitoring for credentials...[/bold green]")

last_size = 0
seen_timestamps = set()

while True:
    if os.path.exists(CAPTURE_FILE):
        try:
            with open(CAPTURE_FILE, "r") as f:
                data = json.load(f)
                
            for entry in data:
                ts = entry.get("timestamp")
                if ts not in seen_timestamps:
                    seen_timestamps.add(ts)
                    console.print(Panel(json.dumps(entry, indent=2), title="[bold red]NEW CAPTURE[/bold red]", border_style="red"))
                    
        except Exception as e:
            pass
            
    time.sleep(1)
