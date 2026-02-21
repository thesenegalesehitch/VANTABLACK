#!/usr/bin/env python3
import sys
import qrcode
import argparse
import os
from PIL import Image, ImageDraw, ImageFont

# Colors
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'

def generate_quishing_payload(url, output_file="attack.png", logo_path=None):
    """
    Generate a malicious QR Code (Quishing)
    """
    print(f"{GREEN}[*] Generating Quishing Payload for: {url}{RESET}")
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
    
    # Add logo if provided
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            
            # Calculate logo size (max 25% of QR code width)
            logo_max_size = int(img.size[0] * 0.25)
            logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
            
            # Calculate position to center the logo
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            
            # Create a white background for the logo to ensure readability
            bg_size = (logo.size[0] + 4, logo.size[1] + 4)
            bg = Image.new('RGBA', bg_size, "white")
            bg_pos = (pos[0] - 2, pos[1] - 2)
            
            img.paste(bg, bg_pos, bg)
            img.paste(logo, pos, logo)
            print(f"{GREEN}[+] Logo embedded.{RESET}")
        except Exception as e:
            print(f"{RED}[!] Error embedding logo: {e}{RESET}")

    # Add deceptive text below
    width, height = img.size
    new_height = height + 60
    final_img = Image.new('RGB', (width, new_height), 'white')
    final_img.paste(img, (0, 0))
    
    draw = ImageDraw.Draw(final_img)
    try:
        # Try to load a nicer font if available, else default
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/liberation/LiberationSans-Bold.ttf"
        ]
        font = None
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, 20)
                    break
                except:
                    continue
        if not font:
            font = ImageFont.load_default()
    except:
        font = None
        
    text = "SCAN TO VERIFY IDENTITY"
    
    # Calculate text position
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
    except:
        text_width = draw.textlength(text, font=font)
        
    draw.text(((width - text_width) / 2, height + 15), text, fill="black", font=font)
    
    final_img.save(output_file)
    print(f"{GREEN}[SUCCESS] Payload saved to: {output_file}{RESET}")
    print(f"{RED}[!] WARNING: Use only for authorized Red Team engagements.{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vantablack Quishing Generator")
    parser.add_argument("--url", required=True, help="Target Phishing URL")
    parser.add_argument("--out", default="payload_qr.png", help="Output filename")
    parser.add_argument("--logo", help="Path to logo image to embed")
    
    args = parser.parse_args()
    
    generate_quishing_payload(args.url, args.out, args.logo)
