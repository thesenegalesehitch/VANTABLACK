#!/usr/bin/env python3
"""
Template Optimization Script for Vantablack
Optimizes all HTML templates for performance, realism, and compatibility
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateOptimizer:
    def __init__(self, templates_dir):
        self.templates_dir = Path(templates_dir)
        self.optimized_count = 0
        
    def optimize_all_templates(self):
        """Optimize all HTML templates in the directory"""
        html_files = list(self.templates_dir.glob("*.html"))
        
        logger.info(f"Found {len(html_files)} templates to optimize")
        
        for html_file in html_files:
            try:
                self.optimize_template(html_file)
                self.optimized_count += 1
                logger.info(f"✓ Optimized {html_file.name}")
            except Exception as e:
                logger.error(f"✗ Failed to optimize {html_file.name}: {e}")
        
        logger.info(f"Optimization complete: {self.optimized_count}/{len(html_files)} templates optimized")
    
    def optimize_template(self, html_file):
        """Optimize a single HTML template"""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Apply optimizations
        self._optimize_styles(soup)
        self._optimize_scripts(soup)
        self._optimize_images(soup)
        self._add_meta_tags(soup)
        self._improve_realism(soup)
        
        # Write optimized content
        optimized_content = soup.prettify()
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
    
    def _optimize_styles(self, soup):
        """Optimize CSS styles"""
        for style in soup.find_all('style'):
            if style.string:
                # Basic CSS minification
                css_content = style.string
                # Remove comments
                css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
                # Remove extra whitespace
                css_content = re.sub(r'\s+', ' ', css_content)
                css_content = css_content.strip()
                style.string = css_content
    
    def _optimize_scripts(self, soup):
        """Optimize JavaScript"""
        for script in soup.find_all('script'):
            if script.get('src'):
                # Add async/defer where appropriate
                if 'phantasm' in script.get('src', '') and not script.get('async'):
                    script['async'] = True
    
    def _optimize_images(self, soup):
        """Optimize images"""
        for img in soup.find_all('img'):
            # Add loading="lazy" for offscreen images
            if not img.get('loading'):
                img['loading'] = 'lazy'
            # Add alt text if missing
            if not img.get('alt') and img.get('src'):
                img['alt'] = ' '
    
    def _add_meta_tags(self, soup):
        """Add essential meta tags"""
        head = soup.find('head')
        if not head:
            return
        
        # Add viewport meta if missing
        viewport = head.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            viewport_tag = soup.new_tag('meta', name='viewport', content='width=device-width, initial-scale=1.0')
            head.append(viewport_tag)
        
        # Add charset meta if missing
        charset = head.find('meta', attrs={'charset': True})
        if not charset:
            charset_tag = soup.new_tag('meta', charset='UTF-8')
            head.insert(0, charset_tag)
    
    def _improve_realism(self, soup):
        """Add realistic touches to the template"""
        # Ensure error message element exists
        if not soup.find(id='error-msg'):
            # Look for potential error container spots
            forms = soup.find_all('form')
            for form in forms:
                error_div = soup.new_tag('div', id='error-msg', 
                                       style='color: #d93025; font-size: 12px; margin: 10px 0; display: none;')
                form.insert(0, error_div)

def main():
    templates_dir = "core/assets/templates/high_fidelity"
    
    if not os.path.exists(templates_dir):
        logger.error(f"Templates directory not found: {templates_dir}")
        return
    
    optimizer = TemplateOptimizer(templates_dir)
    optimizer.optimize_all_templates()

if __name__ == "__main__":
    main()