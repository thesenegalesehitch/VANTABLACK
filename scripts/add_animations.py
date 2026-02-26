#!/usr/bin/env python3
"""
Animation Enhancement Script for Vantablack Templates
Adds realistic micro-interactions and animations to all HTML templates
"""

import os
import re
from pathlib import Path
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnimationEnhancer:
    def __init__(self, templates_dir):
        self.templates_dir = Path(templates_dir)
        self.enhanced_count = 0
        
    def enhance_all_templates(self):
        """Add animations to all HTML templates"""
        html_files = list(self.templates_dir.glob("*.html"))
        
        logger.info(f"Found {len(html_files)} templates to enhance with animations")
        
        for html_file in html_files:
            try:
                self.enhance_template(html_file)
                self.enhanced_count += 1
                logger.info(f"✓ Enhanced {html_file.name} with animations")
            except Exception as e:
                logger.error(f"✗ Failed to enhance {html_file.name}: {e}")
        
        logger.info(f"Animation enhancement complete: {self.enhanced_count}/{len(html_files)} templates enhanced")
    
    def enhance_template(self, html_file):
        """Add animations to a single HTML template"""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Apply animation enhancements
        self._add_animation_css(soup)
        self._enhance_buttons(soup)
        self._enhance_inputs(soup)
        self._add_loading_states(soup)
        self._add_error_animations(soup)
        self._add_social_specific_animations(soup, html_file.name)
        
        # Write enhanced content
        enhanced_content = soup.prettify()
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
    
    def _add_animation_css(self, soup):
        """Add animation CSS link to head"""
        head = soup.find('head')
        if not head:
            return
        
        # Check if animation CSS is already linked
        existing_links = head.find_all('link', rel='stylesheet')
        for link in existing_links:
            if 'animations' in link.get('href', ''):
                return
        
        # Add animation CSS link
        animation_css = soup.new_tag('link', rel='stylesheet', href='/core/assets/css/animations.css')
        head.append(animation_css)
    
    def _enhance_buttons(self, soup):
        """Add animation classes to buttons"""
        button_selectors = [
            'button',
            '.btn',
            '.button',
            '.next-btn',
            '.submit-btn',
            '.btn-primary',
            '.btn-login',
            '[type="submit"]'
        ]
        
        for selector in button_selectors:
            buttons = soup.select(selector)
            for button in buttons:
                classes = button.get('class', [])
                if isinstance(classes, str):
                    classes = [classes]
                
                # Add animation classes
                if 'btn-primary' in classes or 'next-btn' in classes or 'submit-btn' in classes:
                    if 'btn-primary' not in classes:
                        classes.append('btn-primary')
                else:
                    classes.append('btn-primary')
                
                button['class'] = classes
    
    def _enhance_inputs(self, soup):
        """Add animation classes to input fields"""
        inputs = soup.find_all(['input', 'textarea'])
        
        for input_field in inputs:
            if input_field.get('type') in ['text', 'email', 'password', 'tel', 'number']:
                classes = input_field.get('class', [])
                if isinstance(classes, str):
                    classes = [classes]
                
                if 'input-field' not in classes:
                    classes.append('input-field')
                
                input_field['class'] = classes
    
    def _add_loading_states(self, soup):
        """Add loading state support"""
        buttons = soup.find_all('button')
        for button in buttons:
            if button.get('type') == 'submit' or 'submit' in button.get('class', []):
                # Add data attribute for loading text
                if not button.get('data-loading-text'):
                    original_text = button.get_text(strip=True)
                    if original_text and len(original_text) > 0:
                        button['data-loading-text'] = 'Verifying...'
    
    def _add_error_animations(self, soup):
        """Add error animation support"""
        error_divs = soup.find_all(id='error-msg')
        for error_div in error_divs:
            classes = error_div.get('class', [])
            if isinstance(classes, str):
                classes = [classes]
            
            if 'error-message' not in classes:
                classes.append('error-message')
            
            error_div['class'] = classes
    
    def _add_social_specific_animations(self, soup, filename):
        """Add platform-specific animations"""
        # Facebook
        if 'facebook' in filename.lower():
            self._add_facebook_animations(soup)
        # Instagram
        elif 'instagram' in filename.lower():
            self._add_instagram_animations(soup)
        # LinkedIn
        elif 'linkedin' in filename.lower():
            self._add_linkedin_animations(soup)
        # TikTok
        elif 'tiktok' in filename.lower():
            self._add_tiktok_animations(soup)
    
    def _add_facebook_animations(self, soup):
        """Facebook-specific animations"""
        logo = soup.find('img', alt='Facebook')
        if logo:
            classes = logo.get('class', [])
            if isinstance(classes, str):
                classes = [classes]
            classes.append('facebook-like-hover')
            logo['class'] = classes
    
    def _add_instagram_animations(self, soup):
        """Instagram-specific animations"""
        # Add gradient animation to login button
        login_btn = soup.find('button', string=re.compile('Log In', re.I))
        if login_btn:
            classes = login_btn.get('class', [])
            if isinstance(classes, str):
                classes = [classes]
            classes.append('instagram-gradient-shift')
            login_btn['class'] = classes
    
    def _add_linkedin_animations(self, soup):
        """LinkedIn-specific animations"""
        # Add professional glow to cards
        cards = soup.select('.card, .login-container')
        for card in cards:
            classes = card.get('class', [])
            if isinstance(classes, str):
                classes = [classes]
            classes.append('linkedin-professional-glow')
            card['class'] = classes
    
    def _add_tiktok_animations(self, soup):
        """TikTok-specific animations"""
        # Add vibrant pulse to logo
        logo = soup.find('img', alt='TikTok')
        if logo:
            classes = logo.get('class', [])
            if isinstance(classes, str):
                classes = [classes]
            classes.append('tiktok-vibrant-pulse')
            logo['class'] = classes

def main():
    templates_dir = "core/assets/templates/high_fidelity"
    
    if not os.path.exists(templates_dir):
        logger.error(f"Templates directory not found: {templates_dir}")
        return
    
    enhancer = AnimationEnhancer(templates_dir)
    enhancer.enhance_all_templates()

if __name__ == "__main__":
    main()