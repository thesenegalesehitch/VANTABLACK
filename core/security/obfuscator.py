
import re
import random
import string
import base64

class JavaScriptObfuscator:
    """
    Simple polymorphic JavaScript obfuscator to evade static signature detection.
    Replaces variable names with random strings and removes comments.
    """
    
    def __init__(self):
        self.reserved_words = {
            'break', 'case', 'catch', 'class', 'const', 'continue', 'debugger',
            'default', 'delete', 'do', 'else', 'export', 'extends', 'finally',
            'for', 'function', 'if', 'import', 'in', 'instanceof', 'new',
            'return', 'super', 'switch', 'this', 'throw', 'try', 'typeof',
            'var', 'void', 'while', 'with', 'yield', 'let', 'static', 'enum',
            'await', 'implements', 'package', 'protected', 'interface', 'private',
            'public', 'null', 'true', 'false'
        }
        
    def _generate_random_name(self, length=6):
        """Generates a random variable name starting with a letter."""
        first = random.choice(string.ascii_letters)
        rest = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length - 1))
        return first + rest

    def obfuscate(self, js_content: str) -> str:
        """
        Obfuscates the given JavaScript content.
        1. Removes comments
        2. Renames variables/functions (simple approach)
        3. Minifies whitespace
        """
        # 1. Remove comments
        # Remove single line comments // ...
        js_content = re.sub(r'//.*', '', js_content)
        # Remove multi-line comments /* ... */
        js_content = re.sub(r'/\*[\s\S]*?\*/', '', js_content)
        
        # 2. Minify (simple)
        lines = [line.strip() for line in js_content.split('\n') if line.strip()]
        minified = ' '.join(lines)
        
        # 3. Rename specific known variables (Manual mapping for safety)
        # We target specific internal variables of our script to avoid breaking browser APIs
        target_vars = [
            'mouseMoves', 'scrollEvents', 'keyPresses', 'startTime', 'FingerprintCollector', 
            'fp', 'debugInfo', 'canvas', 'ctx', 'baseFonts', 'fontList', 
            'detected', 'span', 'baseWidths', 'detectedCount',
            'components', 'botSignals', 'canvasHash', 'audioHash', 'webgl', 
            'interaction', 'oscillator', 'compressor', 'renderedBuffer'
        ]
        
        mapping = {}
        for var in target_vars:
            mapping[var] = self._generate_random_name()
            
        # Replace whole words only
        for original, new_name in mapping.items():
            pattern = r'\b' + re.escape(original) + r'\b'
            minified = re.sub(pattern, new_name, minified)
            
        return minified

# Global instance
js_obfuscator = JavaScriptObfuscator()
