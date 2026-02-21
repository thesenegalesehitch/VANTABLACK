import sys
import json
from PIL import Image

def decode(path):
    try:
        from pyzbar.pyzbar import decode as zdecode
    except Exception:
        return {"status":"missing_decoder","hint":{"macOS":"brew install zbar && pip install pyzbar","Linux":"sudo apt install -y libzbar0 && pip install pyzbar","Windows":"pip install pyzbar"}}
    try:
        img = Image.open(path)
        res = zdecode(img)
        if not res:
            return {"status":"not_found"}
        return {"status":"ok","data":[r.data.decode(errors="ignore") for r in res]}
    except Exception as e:
        return {"status":"error","message":str(e)}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status":"error","message":"usage: python scripts/qr_tools.py <file>"}, indent=2))
        sys.exit(1)
    r = decode(sys.argv[1])
    print(json.dumps(r, indent=2))

if __name__ == "__main__":
    main()
