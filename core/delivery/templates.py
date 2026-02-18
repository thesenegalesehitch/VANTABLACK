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
try:
    from mjml import mjml_to_html
except Exception:
    mjml_to_html = None  # type: ignore
try:
    import html2text
except Exception:
    html2text = None  # type: ignore

class TemplateEngine:
    def __init__(self):
        self.logger = logging.getLogger("vantablack.delivery.templates")
        self.env = Environment(
            loader=BaseLoader(),
            autoescape=select_autoescape(['html', 'xml'])
        )
        if html2text:
            self.h2t = html2text.HTML2Text()
            self.h2t.ignore_links = False
            self.h2t.ignore_images = True
        else:
            self.h2t = None

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

            if mjml_to_html:
                result = mjml_to_html(rendered_mjml)
                html_content = result.html
            else:
                html_body = rendered_mjml.replace("<mj-text>", "<p>").replace("</mj-text>", "</p>")
                html_body = html_body.replace("<mj-body>", "<body>").replace("</mj-body>", "</body>")
                html_body = html_body.replace("<mj-section>", "<section>").replace("</mj-section>", "</section>")
                html_body = html_body.replace("<mj-column>", "<div>").replace("</mj-column>", "</div>")
                html_content = f"<html>{html_body}</html>"

            # 3. Generate Plain Text fallback
            if self.h2t:
                text_content = self.h2t.handle(html_content)
            else:
                text_content = " ".join(html_content.replace("<", " <").split(">"))

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
