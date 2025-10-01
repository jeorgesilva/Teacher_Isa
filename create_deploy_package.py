# English Teacher Bot - Compress for Cloud Deployment
# ==================================================

import os
import tarfile
import zipfile
from pathlib import Path
import shutil

def create_deployment_package():
    """Cria pacote completo para deploy em VM."""
    
    # Diretório atual
    current_dir = Path(".")
    
    # Arquivos essenciais para incluir
    essential_files = [
        "english_teacher_bot.py",
        "english_teacher_production.py",
        "instagram_reels.py", 
        "requirements.txt",
        "config.txt",
        "setup.sh",
        "DEPLOYMENT_GUIDE.md"
    ]
    
    # Diretórios para incluir
    essential_dirs = [
        "reels_content",
        "data"
    ]
    
    print("🎓 Creating English Teacher Bot deployment package...")
    
    # Criar arquivo tar.gz
    with tarfile.open("english_teacher_bot_deploy.tar.gz", "w:gz") as tar:
        
        # Adicionar arquivos essenciais
        for file in essential_files:
            if Path(file).exists():
                tar.add(file)
                print(f"✅ Added: {file}")
            else:
                print(f"⚠️  Missing: {file}")
        
        # Adicionar diretórios
        for dir_name in essential_dirs:
            if Path(dir_name).exists():
                tar.add(dir_name)
                print(f"✅ Added directory: {dir_name}")
            else:
                print(f"⚠️  Missing directory: {dir_name}")
    
    # Criar arquivo zip também (Windows compatibility)
    with zipfile.ZipFile("english_teacher_bot_deploy.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        
        for file in essential_files:
            if Path(file).exists():
                zipf.write(file)
        
        for dir_name in essential_dirs:
            if Path(dir_name).exists():
                for file_path in Path(dir_name).rglob("*"):
                    if file_path.is_file():
                        zipf.write(file_path)
    
    print("\n📦 Deployment packages created:")
    print("- english_teacher_bot_deploy.tar.gz (Linux/Mac)")
    print("- english_teacher_bot_deploy.zip (Windows)")
    
    # Criar README de deployment
    readme_content = """# English Teacher Bot - Deployment Package
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
"""
    
    with open("DEPLOY_README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ Created DEPLOY_README.md")
    
    print("\n🎯 Ready for deployment!")
    print("Upload the .tar.gz file to your server and follow DEPLOY_README.md")

if __name__ == "__main__":
    create_deployment_package()