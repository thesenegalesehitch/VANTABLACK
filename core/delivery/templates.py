"""
Vantablack Core v5 - Template Rendering Engine
==============================================

Handles:
- MJML to HTML compilation (responsive emails)
- Jinja2 context injection (dynamic variables)
- Auto-text version generation
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from jinja2 import Environment, BaseLoader, select_autoescape
from mjml import mjml_to_html
import html2text

class TemplateEngine:
    def __init__(self):
        self.logger = logging.getLogger("vantablack.delivery.templates")
        self.env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = True

    def render(self, mjml_content: str, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Render MJML template with Jinja2 context.
        Returns both HTML and Plain Text versions.
        """
        try:
            # 1. Inject variables into MJML (Jinja2 first)
            # This allows dynamic MJML structures
            template = self.env.from_string(mjml_content)
            rendered_mjml = template.render(**context)

            # 2. Compile MJML to HTML
            # Note: mjml_to_html is synchronous, might need threadpool for high volume
            result = mjml_to_html(rendered_mjml)
            html_content = result.html

            # 3. Generate Plain Text fallback
            text_content = self.h2t.handle(html_content)

            return {
                "html": html_content,
                "text": text_content,
                "mjml": rendered_mjml
            }
            
        except Exception as e:
            self.logger.error(f"Template rendering failed: {str(e)}")
            raise

    async def render_async(self, mjml_content: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Async wrapper for render method"""
        return await asyncio.to_thread(self.render, mjml_content, context)
