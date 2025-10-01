# English Teacher Bot - Complete Deployment Guide
## 🎓 Production-Ready English Learning Assistant

### 📋 Project Overview

This bot helps English learners with:
- **Interactive Conversations** - AI-powered English practice
- **Daily Educational Posts** - Motivational content with learning tips
- **Instagram Reels Integration** - Automated sharing from @englishwithmrjay
- **Professional Call-to-Actions** - Links to premium English resources

### 🏗️ Architecture

```
english_teacher_bot/
├── english_teacher_bot.py         # Main conversational bot
├── english_teacher_production.py  # Production version (RECOMMENDED)
├── instagram_reels.py             # Reels integration system
├── requirements.txt               # Python dependencies
├── config.txt                     # Configuration guidelines
├── reels_content/                 # Folder for Instagram reels
├── data/                          # User data storage
└── logs/                          # Log files (auto-created)
```

### 🚀 Quick Setup Guide

#### 1. **Create Bot Token**
```bash
# Talk to @BotFather on Telegram
# Create new bot: /newbot
# Save token to file:
echo "YOUR_BOT_TOKEN_HERE" > token.txt
```

#### 2. **Get Gemini API Key**
```bash
# Go to: https://makersuite.google.com/app/apikey
# Generate API key
# Save to file:
echo "YOUR_GEMINI_API_KEY" > apikey.txt
```

#### 3. **Configure Group/Channel**
```python
# Edit the GROUP_ID in production file:
GROUP_ID = "@your_english_channel"  # or numeric ID like -1001234567890

# Add your Telegram ID:
ADMIN_IDS = [YOUR_TELEGRAM_ID]
```

#### 4. **Install Dependencies**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install requirements
pip install -r requirements.txt
```

#### 5. **Run the Bot**
```bash
# For development:
python english_teacher_bot.py

# For production (RECOMMENDED):
python english_teacher_production.py
```

---

## 🌐 VM Deployment Instructions

### ☁️ **For Digital Ocean, AWS, Google Cloud, etc.**

#### 1. **Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv git -y

# Clone or upload your project
git clone YOUR_REPO_URL
# or upload files via SCP/FTP
```

#### 2. **Project Configuration**
```bash
# Navigate to project
cd english_teacher_bot/

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create configuration files
echo "YOUR_BOT_TOKEN" > token.txt
echo "YOUR_GEMINI_API_KEY" > apikey.txt
```

#### 3. **Configure for Production**
```bash
# Edit the production file
nano english_teacher_production.py

# Set your configurations:
GROUP_ID = "@your_channel"
ADMIN_IDS = [your_telegram_id]
```

#### 4. **Run with SystemD (Auto-restart)**
```bash
# Create service file
sudo nano /etc/systemd/system/english-teacher-bot.service
```

**Service file content:**
```ini
[Unit]
Description=English Teacher Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/english_teacher_bot
Environment=PATH=/home/ubuntu/english_teacher_bot/venv/bin
ExecStart=/home/ubuntu/english_teacher_bot/venv/bin/python english_teacher_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable english-teacher-bot.service
sudo systemctl start english-teacher-bot.service

# Check status
sudo systemctl status english-teacher-bot.service
```

#### 5. **Monitor Logs**
```bash
# View live logs
sudo journalctl -u english-teacher-bot.service -f

# View bot logs
tail -f bot.log
```

---

## 📱 **Instagram Reels Integration**

### Option 1: Manual Upload (Recommended)
1. Download reels from @englishwithmrjay manually
2. Place videos in `reels_content/` folder
3. Bot will automatically post them with educational comments

### Option 2: Automated (Advanced)
```bash
# Install yt-dlp for Instagram downloads
pip install yt-dlp

# Note: May require Instagram authentication
# Use responsibly and respect Instagram's terms
```

---

## 🔧 **Configuration Details**

### **Core Settings**
```python
# In english_teacher_production.py:

GROUP_ID = "@your_english_channel"    # Your channel/group
ADMIN_IDS = [123456789]               # Your Telegram ID
MAIN_LINK = "https://linktr.ee/..."   # Your course/resource link
```

### **Posting Schedule**
- **09:00 AM** - Daily educational post with motivation and tips

### **Commands Available**
**For Students:**
- `/start` - Welcome message with menu
- `/tips` - English learning tips
- `/motivation` - Daily motivation
- `/resources` - Access premium content
- `/practice` - Start conversation practice

**For Admins:**
- `/health` - System health status
- `/post_now` - Send educational post immediately

---

## 🛡️ **Security & Best Practices**

### **Environment Variables (Recommended)**
```bash
# Instead of files, use environment variables:
export TELEGRAM_BOT_TOKEN="your_token"
export GEMINI_API_KEY="your_gemini_key"
export GROUP_ID="@your_channel"
export ADMIN_IDS="123456789,987654321"
```

### **Firewall Configuration**
```bash
# Basic firewall setup
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### **SSL/HTTPS (if using webhooks)**
```bash
# Install certbot for free SSL
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com
```

---

## 📊 **Monitoring & Maintenance**

### **Health Checks**
```bash
# Check if bot is running
sudo systemctl status english-teacher-bot

# View recent logs
sudo journalctl -u english-teacher-bot -n 50

# Monitor resource usage
htop
```

### **Log Rotation**
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/english-teacher-bot
```

```
/home/ubuntu/english_teacher_bot/bot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

### **Backup Strategy**
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup_${DATE}.tar.gz english_teacher_bot/
# Upload to cloud storage
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### Bot not responding:
```bash
# Check service status
sudo systemctl status english-teacher-bot

# Restart service
sudo systemctl restart english-teacher-bot

# Check logs
sudo journalctl -u english-teacher-bot -f
```

#### Network errors:
- The production version has automatic retry logic
- Check internet connectivity
- Verify Telegram API access

#### AI responses failing:
- Bot has fallback responses when Gemini fails
- Check API key validity
- Monitor API quota usage

### **Emergency Commands**
```bash
# Stop bot
sudo systemctl stop english-teacher-bot

# Restart bot
sudo systemctl restart english-teacher-bot

# View error logs
grep ERROR bot.log

# Check disk space
df -h
```

---

## 💰 **Cost Optimization**

### **Free Tier Options**
- **Digital Ocean:** $5/month droplet
- **AWS EC2:** t2.micro (free tier)
- **Google Cloud:** e2-micro (free tier)
- **Oracle Cloud:** Always free tier

### **Resource Requirements**
- **RAM:** 512MB minimum, 1GB recommended
- **Storage:** 10GB minimum
- **CPU:** 1 vCPU sufficient
- **Bandwidth:** ~100MB/month typical usage

---

## 📞 **Support & Updates**

### **Getting Help**
1. Check logs first: `tail -f bot.log`
2. Use admin command `/health` in Telegram
3. Review this documentation
4. Check system resources: `htop`

### **Updates**
```bash
# Pull latest code
git pull origin main

# Restart service
sudo systemctl restart english-teacher-bot
```

---

## ✅ **Pre-Launch Checklist**

- [ ] Bot token configured
- [ ] Gemini API key set up
- [ ] GROUP_ID configured  
- [ ] ADMIN_IDS added
- [ ] Dependencies installed
- [ ] Service file created
- [ ] Bot tested locally
- [ ] Firewall configured
- [ ] Logs monitoring set up
- [ ] Backup strategy in place

**🎉 Your English Teacher Bot is ready for production! 🚀**

---

## 📋 **Quick Commands Summary**

```bash
# Start development
python english_teacher_bot.py

# Start production
python english_teacher_production.py

# System service commands
sudo systemctl start english-teacher-bot
sudo systemctl stop english-teacher-bot  
sudo systemctl restart english-teacher-bot
sudo systemctl status english-teacher-bot

# Monitoring
sudo journalctl -u english-teacher-bot -f
tail -f bot.log

# Health check via Telegram
/health
```

**Happy teaching! 🎓📚**