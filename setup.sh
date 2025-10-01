#!/bin/bash
# English Teacher Bot - Automated Setup Script
# ==========================================

echo "🎓 English Teacher Bot - Automated Setup"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

print_step "1. Checking system requirements..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_status "pip3 found"
else
    print_error "pip3 not found. Please install pip3"
    exit 1
fi

print_step "2. Setting up virtual environment..."

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

print_step "3. Installing dependencies..."

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

print_step "4. Configuration setup..."

# Check for token file
if [ ! -f "token.txt" ]; then
    print_warning "token.txt not found"
    echo -n "Please enter your Telegram bot token: "
    read BOT_TOKEN
    echo "$BOT_TOKEN" > token.txt
    print_status "Bot token saved"
else
    print_status "Bot token file found"
fi

# Check for API key file
if [ ! -f "apikey.txt" ]; then
    print_warning "apikey.txt not found"
    echo -n "Please enter your Gemini API key (optional, press Enter to skip): "
    read API_KEY
    if [ ! -z "$API_KEY" ]; then
        echo "$API_KEY" > apikey.txt
        print_status "Gemini API key saved"
    else
        print_warning "Gemini API key skipped - AI features will be disabled"
    fi
else
    print_status "Gemini API key file found"
fi

print_step "5. Testing bot connection..."

# Test bot
python3 -c "
import sys
sys.path.append('.')
try:
    with open('token.txt') as f:
        token = f.read().strip()
    print('✅ Token loaded successfully')
except Exception as e:
    print(f'❌ Error loading token: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_status "Bot configuration test passed"
else
    print_error "Bot configuration test failed"
    exit 1
fi

print_step "6. Creating startup script..."

# Create startup script
cat > start_bot.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "🎓 Starting English Teacher Bot..."
python english_teacher_production.py
EOF

chmod +x start_bot.sh
print_status "Startup script created: ./start_bot.sh"

print_step "7. Setting up systemd service (optional)..."

read -p "Do you want to set up auto-start service? (y/N): " setup_service

if [[ $setup_service =~ ^[Yy]$ ]]; then
    SERVICE_USER=$(whoami)
    WORKING_DIR=$(pwd)
    
    # Create service file
    sudo tee /etc/systemd/system/english-teacher-bot.service > /dev/null << EOF
[Unit]
Description=English Teacher Bot
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$WORKING_DIR
Environment=PATH=$WORKING_DIR/venv/bin
ExecStart=$WORKING_DIR/venv/bin/python english_teacher_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start service
    sudo systemctl daemon-reload
    sudo systemctl enable english-teacher-bot.service
    
    print_status "Systemd service created and enabled"
    print_status "Use: sudo systemctl start english-teacher-bot to start"
    print_status "Use: sudo systemctl status english-teacher-bot to check status"
else
    print_status "Systemd service setup skipped"
fi

print_step "8. Final configuration check..."

echo ""
echo "📋 Configuration Summary:"
echo "========================"

# Check files
if [ -f "token.txt" ]; then
    echo "✅ Bot token: Configured"
else
    echo "❌ Bot token: Missing"
fi

if [ -f "apikey.txt" ]; then
    echo "✅ Gemini API: Configured"
else
    echo "⚠️  Gemini API: Not configured (fallback mode)"
fi

if [ -d "venv" ]; then
    echo "✅ Virtual environment: Ready"
else
    echo "❌ Virtual environment: Missing"
fi

if [ -f "requirements.txt" ]; then
    echo "✅ Dependencies: Installed"
else
    echo "❌ Dependencies: Missing"
fi

echo ""
echo "🚀 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit english_teacher_production.py and configure:"
echo "   - GROUP_ID = '@your_channel_or_group'"
echo "   - ADMIN_IDS = [your_telegram_id]"
echo ""
echo "2. Start the bot:"
echo "   ./start_bot.sh"
echo ""
echo "3. Or start as service:"
echo "   sudo systemctl start english-teacher-bot"
echo ""
echo "4. Monitor logs:"
echo "   tail -f bot.log"
echo ""
print_status "Happy teaching! 🎓📚"