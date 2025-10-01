# English Teacher Bot - Deployment Package
## 🚀 Quick Deploy Instructions

### 1. Upload to your server:
```bash
scp english_teacher_bot_deploy.tar.gz user@your-server:~/
```

### 2. Extract on server:
```bash
ssh user@your-server
tar -xzf english_teacher_bot_deploy.tar.gz
cd english_teacher_bot/
```

### 3. Run setup:
```bash
chmod +x setup.sh
./setup.sh
```

### 4. Configure:
```bash
# Edit configuration
nano english_teacher_production.py

# Set GROUP_ID and ADMIN_IDS
```

### 5. Start bot:
```bash
./start_bot.sh
# OR
sudo systemctl start english-teacher-bot
```

### 📋 What's included:
- Complete bot system
- Production-ready code
- Auto-setup script
- Deployment guide
- Service configuration
- Error handling & retry logic

### 🔧 Requirements:
- Ubuntu/Debian server
- Python 3.8+
- Internet connection
- Telegram bot token
- (Optional) Gemini API key

**Ready to teach English! 🎓📚**
