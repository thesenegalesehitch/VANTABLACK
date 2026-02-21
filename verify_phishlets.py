import os
import yaml
import sys

def verify_phishlets():
    phishlets_dir = "phishlets"
    if not os.path.exists(phishlets_dir):
        print(f"Directory {phishlets_dir} not found!")
        return

    files = [f for f in os.listdir(phishlets_dir) if f.endswith(".yaml")]
    if not files:
        print(f"No phishlet files found in {phishlets_dir}")
        return

    print(f"Found {len(files)} phishlet definitions.")
    print("-" * 50)

    required_keys = ["name", "author", "min_ver", "proxy_hosts", "auth_tokens", "credentials"]
    
    valid_count = 0
    invalid_count = 0

    for filename in files:
        filepath = os.path.join(phishlets_dir, filename)
        try:
            with open(filepath, "r") as f:
                data = yaml.safe_load(f)
                
            if not data:
                print(f"[!] {filename}: Empty file or invalid YAML")
                invalid_count += 1
                continue

            missing_keys = [key for key in required_keys if key not in data]
            
            # Check for either landing_path OR login configuration
            has_landing = "landing_path" in data or "login" in data
            
            if missing_keys:
                print(f"[!] {filename}: Missing keys: {', '.join(missing_keys)}")
                invalid_count += 1
            elif not has_landing:
                print(f"[!] {filename}: Missing landing configuration (landing_path or login)")
                invalid_count += 1
            else:
                print(f"[+] {filename}: Valid structure (Name: {data.get('name')}, Author: {data.get('author')})")
                valid_count += 1
                
        except Exception as e:
            print(f"[!] {filename}: YAML Error: {e}")
            invalid_count += 1

    print("-" * 50)
    print(f"Summary: {valid_count} Valid, {invalid_count} Invalid")
    
    if invalid_count == 0:
        print("\nAll phishlets are correctly configured and ready for deployment.")
    else:
        print(f"\nFound {invalid_count} phishlets with configuration errors.")

if __name__ == "__main__":
    verify_phishlets()
