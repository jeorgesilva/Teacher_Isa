# 🌐 Teacher Isa Bot - Deploy no Google Cloud Platform

## 🚀 **GUIA COMPLETO PARA DEPLOY NA VM**

### 📋 **Pré-requisitos:**
- ✅ VM criada no Google Cloud
- ✅ SSH configurado
- ✅ Pacote do bot já criado no Desktop

---

## 🔧 **PASSO 1: Preparar a VM**

### **1.1 Conectar à VM:**
```bash
# Pelo console web do Google Cloud
# Ou via SSH local (se configurou chaves)
gcloud compute ssh your-vm-name --zone=your-zone
```

### **1.2 Atualizar sistema:**
```bash
sudo apt update && sudo apt upgrade -y
```

### **1.3 Instalar Docker:**
```bash
# Instalar Docker
sudo apt install -y docker.io docker-compose

# Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Relogar para aplicar grupo
exit
# Conectar novamente à VM
```

---

## 📤 **PASSO 2: Upload dos Arquivos**

### **2.1 Usando SCP (do seu Mac):**
```bash
# No seu Mac, no terminal
cd ~/Desktop

# Upload do arquivo ZIP
scp teacher_isa_bot_deploy_*.zip username@VM-EXTERNAL-IP:/home/username/

# Ou upload da pasta completa
scp -r teacher_isa_bot_deploy_*/ username@VM-EXTERNAL-IP:/home/username/
```

### **2.2 Usando console web do Google Cloud:**
```bash
# 1. Ir para Compute Engine > VM instances
# 2. Clicar em SSH na sua VM
# 3. No terminal da VM, executar:
wget --version  # Verificar se wget está disponível

# Se não estiver, instalar:
sudo apt install wget -y
```

### **2.3 Alternativa - Upload direto via terminal da VM:**
```bash
# Na VM, criar arquivo para o código
nano teacher_isa_bot.py
# Copiar e colar o código completo do bot

# Criar arquivos de configuração
echo "8229862045:AAEQne8UiRruR84qCpjmrpEpon-yE-8A3Cs" > token.txt
echo "SUA_GEMINI_API_KEY" > apikey.txt
```

---

## 🐳 **PASSO 3: Deploy Automático**

### **3.1 Descompactar (se enviou ZIP):**
```bash
# Na VM
unzip teacher_isa_bot_deploy_*.zip
cd teacher_isa_bot_deploy_*/
```

### **3.2 Executar deploy:**
```bash
# Dar permissão de execução
chmod +x deploy.sh monitor.sh

# Executar deploy automático
sudo ./deploy.sh
```

### **3.3 Verificar se funcionou:**
```bash
# Ver status
sudo docker-compose ps

# Ver logs
sudo docker-compose logs -f teacher-isa-bot
```

---

## 📱 **PASSO 4: Configuração Manual (se necessário)**

### **4.1 Se não tem o pacote, criar manualmente:**
```bash
# Criar diretório
mkdir teacher_isa_bot
cd teacher_isa_bot

# Criar requirements.txt
cat > requirements.txt << EOF
python-telegram-bot==21.0.1
google-generativeai==0.8.3
asyncio
pathlib
datetime
logging
random
traceback
os
sys
time
EOF

# Criar Dockerfile
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY teacher_isa_bot.py .
COPY token.txt .
COPY apikey.txt .

RUN mkdir -p reels_content

CMD ["python", "teacher_isa_bot.py"]
EOF

# Criar docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'

services:
  teacher-isa-bot:
    build: .
    container_name: teacher_isa_bot
    restart: unless-stopped
    volumes:
      - ./reels_content:/app/reels_content
      - ./logs:/app/logs
    environment:
      - TZ=America/Sao_Paulo
    networks:
      - bot_network

networks:
  bot_network:
    driver: bridge
EOF
```

### **4.2 Criar arquivos de configuração:**
```bash
# Token do bot
echo "8229862045:AAEQne8UiRruR84qCpjmrpEpon-yE-8A3Cs" > token.txt

# API Key do Gemini (substitua pela sua)
echo "SUA_GEMINI_API_KEY_AQUI" > apikey.txt

# Criar pasta para vídeos
mkdir -p reels_content
```

### **4.3 Copiar código do bot:**
```bash
# Criar arquivo do bot
nano teacher_isa_bot.py
# Copiar e colar todo o código do arquivo teacher_isa_bot.py
```

---

## 🚀 **PASSO 5: Executar o Bot**

### **5.1 Build e start:**
```bash
# Construir e iniciar
sudo docker-compose up --build -d

# Verificar status
sudo docker-compose ps
sudo docker-compose logs teacher-isa-bot
```

### **5.2 Monitorar:**
```bash
# Logs em tempo real
sudo docker-compose logs -f

# Status detalhado
sudo docker stats teacher_isa_bot

# Verificar se está respondendo
# Envie /health para o bot no Telegram
```

---

## 📹 **PASSO 6: Adicionar Vídeos (Opcional)**

### **6.1 Upload de vídeos:**
```bash
# Na VM, criar pasta
mkdir -p reels_content

# Upload vídeos do seu Mac
scp video*.mp4 username@VM-IP:/home/username/teacher_isa_bot/reels_content/

# Ou baixar diretamente na VM usando yt-dlp:
sudo apt install python3-pip -y
pip3 install yt-dlp

# Baixar vídeos do Instagram (exemplo)
yt-dlp "https://www.instagram.com/reel/XXXXX/" -o "reels_content/%(title)s.%(ext)s"
```

### **6.2 Reiniciar para reconhecer vídeos:**
```bash
sudo docker-compose restart
```

---

## 🔥 **COMANDOS ÚTEIS PARA MANUTENÇÃO**

### **Gerenciamento:**
```bash
# Parar bot
sudo docker-compose down

# Iniciar bot
sudo docker-compose up -d

# Reiniciar bot
sudo docker-compose restart

# Ver logs específicos
sudo docker-compose logs teacher-isa-bot --tail=50

# Entrar no container
sudo docker exec -it teacher_isa_bot bash
```

### **Monitoramento:**
```bash
# Status geral
sudo docker-compose ps

# Uso de recursos
sudo docker stats

# Espaço em disco
df -h

# Memória
free -h

# Processos
top
```

### **Backup:**
```bash
# Backup completo
tar -czf backup_$(date +%Y%m%d).tar.gz teacher_isa_bot/

# Backup só configurações
cp token.txt apikey.txt ~/backup/
```

---

## 🛡️ **SEGURANÇA E CONFIGURAÇÕES**

### **Firewall:**
```bash
# Configurar firewall básico
sudo ufw allow ssh
sudo ufw enable
sudo ufw status
```

### **Updates automáticos:**
```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure unattended-upgrades
```

### **Logs:**
```bash
# Limitar tamanho dos logs
echo '{"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"}}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

---

## 📊 **VERIFICAÇÃO FINAL**

### **✅ Checklist de funcionamento:**
1. **VM online:** `ping VM-IP`
2. **Docker rodando:** `sudo docker ps`
3. **Bot container ativo:** `sudo docker-compose ps`
4. **Logs sem erro:** `sudo docker-compose logs`
5. **Bot responde:** Enviar `/start` no Telegram
6. **Posts automáticos:** Aguardar horários (9h, 12h, 15h, 18h, 21h)

### **🎯 Configurações atuais:**
- **Bot:** @teacher_isa_bot
- **Grupo:** @English_teacher  
- **Horários:** 9h(vídeo) | 12h,15h,18h(quiz) | 21h(curiosidade)
- **IA:** Gemini 2.5 Flash
- **Quiz Polls:** Ativos e funcionando

---

## 🆘 **TROUBLESHOOTING**

### **Bot não inicia:**
```bash
# Verificar logs
sudo docker-compose logs teacher-isa-bot

# Verificar arquivos
ls -la token.txt apikey.txt

# Verificar configuração
sudo docker-compose config
```

### **Erro de memória:**
```bash
# Verificar uso de RAM
free -h

# Adicionar swap se necessário
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### **Bot para sozinho:**
```bash
# Configurar restart automático
# (já configurado no docker-compose.yml com restart: unless-stopped)

# Verificar logs de sistema
sudo journalctl -u docker.service
```

---

## 🎉 **RESULTADO FINAL**

Após seguir todos os passos, você terá:

- ✅ **Teacher Isa Bot rodando 24/7** na Google Cloud
- ✅ **Quiz polls interativos** funcionando
- ✅ **IA conversacional** ativa
- ✅ **Posts automáticos** nos horários programados
- ✅ **Sistema robusto** com restart automático
- ✅ **Monitoramento** em tempo real

**🚀 Seu bot está pronto para ensinar inglês para milhares de alunos! 🎓✨**

---

## 📞 **Comandos de Teste**

Após o deploy, teste no Telegram:
- `/start` - Verificar se bot responde
- `/quiz` - Testar quiz polls
- `/health` - Status do sistema (admin)
- `/help` - Ver todos os comandos

**Seu Teacher Isa Bot está oficialmente na nuvem! 🌐🎓**