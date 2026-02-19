"""
Vantablack Core v5 - Mutation Engine
====================================

Handles:
- Polymorphic obfuscation of Javascript (AST based)
- HTML structure mutation (tag randomization, class renaming)
- CSS selector rewriting
"""

import re
import random
import string
import logging
from typing import Dict, List
from bs4 import BeautifulSoup
import jsbeautifier

class MutationEngine:
    def __init__(self):
        self.logger = logging.getLogger("vantablack.mutation.engine")
        self._class_map: Dict[str, str] = {}
        self._id_map: Dict[str, str] = {}

    def generate_random_name(self, length: int = 8) -> str:
        """Generate a random variable/class name"""
        chars = string.ascii_letters
        return ''.join(random.choice(chars) for _ in range(length))

    def mutate_html(self, html_content: str) -> str:
        """
        Mutate HTML structure:
        - Rename classes and IDs
        - Inject dummy comments/tags
        - Shuffle attributes
        - Inject Junk Code (Polymorphism)
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Rename Classes
        for tag in soup.find_all(class_=True):
            new_classes = []
            for cls in tag['class']:
                if cls not in self._class_map:
                    self._class_map[cls] = self.generate_random_name()
                new_classes.append(self._class_map[cls])
            tag['class'] = new_classes
            
        # 2. Rename IDs
        for tag in soup.find_all(id=True):
            old_id = tag['id']
            if old_id not in self._id_map:
                self._id_map[old_id] = self.generate_random_name()
            tag['id'] = self._id_map[old_id]

        # 3. Inject Noise (Invisible elements)
        body = soup.find('body')
        if body:
            # Inject at top
            noise_top = soup.new_tag('div', style="display:none; visibility:hidden; opacity:0;")
            noise_top.string = self.generate_random_name(64)
            body.insert(0, noise_top)
            
            # Inject random junk scripts
            junk_script = soup.new_tag('script')
            junk_script.string = f"var {self.generate_random_name()} = '{self.generate_random_name(128)}';"
            body.append(junk_script)

        # 4. Inject Random Data Attributes (Evasion)
        for tag in soup.find_all():
            if random.random() < 0.3:  # 30% chance per tag
                attr_name = f"data-{self.generate_random_name(4).lower()}"
                tag[attr_name] = self.generate_random_name(8)
            
        return str(soup)

    def mutate_js(self, js_content: str) -> str:
        """
        Advanced JS obfuscation:
        - String splitting
        - Variable renaming (Simulated)
        - Dead code injection
        - Control flow flattening (Simulated)
        """
        # 1. Split Strings
        def split_string(match):
            s = match.group(1)
            if len(s) > 4:
                chunks = [s[i:i+4] for i in range(0, len(s), 4)]
                return " + ".join([f"'{chunk}'" for chunk in chunks])
            return f"'{s}'"
            
        obfuscated = re.sub(r"'([^']*)'", split_string, js_content)
        
        # 2. Remove comments
        obfuscated = re.sub(r"//.*", "", obfuscated)
        obfuscated = re.sub(r"/\*[\s\S]*?\*/", "", obfuscated)
        
        # 3. Inject Dead Code
        dead_code = f"""
        (function(){{
            var _0x{self.generate_random_name(4)} = ['{self.generate_random_name(5)}', '{self.generate_random_name(5)}'];
            var _0y{self.generate_random_name(4)} = function(_0z) {{ return _0z; }};
        }})();
        """
        obfuscated = dead_code + obfuscated
        
        # 4. Minify/Beautify to change structure
        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        return jsbeautifier.beautify(obfuscated, opts)

    def get_maps(self) -> Dict:
        """Return the mapping used for current mutation context"""
        return {"classes": self._class_map, "ids": self._id_map}
