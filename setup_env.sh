#!/bin/bash

# Configuration
VENV_DIR="venv"
PYTHON="python3"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[*] Vantablack Automated Environment Setup${NC}"

# Check Python
if ! command -v $PYTHON &> /dev/null; then
    echo -e "${RED}[!] Python 3 is required but not found.${NC}"
    exit 1
fi

# Create Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${GREEN}[+] Creating virtual environment ($VENV_DIR)...${NC}"
    $PYTHON -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo -e "${RED}[!] Failed to create virtual environment.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}[*] Virtual environment already exists.${NC}"
fi

# Activate and Install
echo -e "${GREEN}[+] Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

echo -e "${GREEN}[+] Upgrading pip...${NC}"
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}[+] Installing dependencies from requirements.txt...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[!] Failed to install dependencies.${NC}"
        exit 1
    fi
else
    echo -e "${RED}[!] requirements.txt not found!${NC}"
    exit 1
fi

# Create launcher script
echo -e "${GREEN}[+] Creating launcher script (vanta.sh)...${NC}"
cat > vanta.sh << 'EOF'
#!/bin/bash
# Vantablack CLI Launcher
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "$DIR/venv/bin/activate"
export PYTHONPATH="$DIR:$PYTHONPATH"
python3 -m core.cli.main "$@"
EOF

chmod +x vanta.sh

echo -e "${GREEN}[SUCCESS] Setup complete!${NC}"
echo -e "${GREEN}[*] You can now use './vanta.sh' to run commands without errors.${NC}"
echo -e "${GREEN}[*] Example: ./vanta.sh --help${NC}"
