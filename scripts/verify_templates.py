import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.social.templates import TemplateLoader

def verify():
    templates = TemplateLoader.load_all()
    print(f"Loaded {len(templates)} templates.")
    
    if "teams_meeting" in templates:
        print("✅ teams_meeting template found.")
        tmpl = templates["teams_meeting"]
        print(f"Target URL: {tmpl.target_url}")
        
        # Test render
        html = tmpl.render({"session_id": "TEST_SESS", "campaign_id": "TEST_CAMP"})
        if "Microsoft Teams" in html and "TEST_SESS" in html:
             print("✅ Render check passed.")
        else:
             print("❌ Render check failed.")
    else:
        print("❌ teams_meeting template NOT found.")

if __name__ == "__main__":
    verify()