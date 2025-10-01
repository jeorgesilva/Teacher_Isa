# 🚀 DEPLOY RÁPIDO NO GOOGLE CLOUD - Teacher Isa Bot

## ⚡ **MÉTODO AUTOMÁTICO (RECOMENDADO)**

### 📋 **Pré-requisitos:**
1. ✅ VM criada no Google Cloud
2. ✅ gcloud CLI instalado no seu Mac
3. ✅ SSH configurado para a VM

### 🚀 **Deploy em 1 comando:**
```bash
cd "/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot"
./upload_to_gcloud.sh
```

**O script vai:**
- 📤 Fazer upload automático do pacote
- 🐳 Instalar Docker na VM
- 🚀 Fazer deploy completo
- ✅ Deixar o bot rodando

---

## 🔧 **MÉTODO MANUAL (PASSO A PASSO)**

### **1. Conectar à VM:**
```bash
# Pelo console web do Google Cloud
# Clicar em SSH na sua VM
```

### **2. Preparar VM:**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### **3. Upload dos arquivos:**

#### **Opção A - Via console web:**
```bash
# 1. Abrir terminal da VM no navegador
# 2. Criar arquivo do bot:
nano teacher_isa_bot.py
# 3. Copiar e colar todo o código
# 4. Salvar com Ctrl+X, Y, Enter
```

#### **Opção B - Via gcloud (do seu Mac):**
```bash
# Upload do pacote ZIP
cd ~/Desktop
gcloud compute scp teacher_isa_bot_deploy_*.zip SEU-USUARIO@SUA-VM:/home/SEU-USUARIO/ --zone=SUA-ZONA
```

### **4. Configurar na VM:**
```bash
# Descompactar
unzip teacher_isa_bot_deploy_*.zip
cd teacher_isa_bot_deploy_*/

# Verificar arquivos
ls -la

# Executar deploy
chmod +x deploy.sh
sudo ./deploy.sh
```

### **5. Verificar funcionamento:**
```bash
# Status
sudo docker-compose ps

# Logs
sudo docker-compose logs -f

# Monitorar
chmod +x monitor.sh
sudo ./monitor.sh
```

---

## 📱 **TESTE NO TELEGRAM**

### **Comandos para testar:**
- `/start` - Verificar se bot responde
- `/quiz` - Testar quiz polls
- `/help` - Ver comandos disponíveis
- `/health` - Status (apenas admins)

---

## 🛠️ **COMANDOS ÚTEIS**

### **Conectar à VM:**
```bash
gcloud compute ssh SEU-USUARIO@SUA-VM --zone=SUA-ZONA
```

### **Gerenciar bot:**
```bash
# Parar bot
sudo docker-compose down

# Iniciar bot
sudo docker-compose up -d

# Reiniciar bot
sudo docker-compose restart

# Ver logs
sudo docker-compose logs -f
```

### **Status da VM:**
```bash
# Uso de recursos
sudo docker stats

# Espaço em disco
df -h

# Memória
free -h
```

---

## 📊 **CONFIGURAÇÃO ATUAL**

### ✅ **Bot pronto com:**
- **Nome:** @teacher_isa_bot
- **Token:** 8229862045:AAEQne8UiRruR84qCpjmrpEpon-yE-8A3Cs
- **Grupo:** @English_teacher
- **IA:** Gemini 2.5 Flash
- **Quiz Polls:** Ativos
- **Horários:** 9h(vídeo) | 12h,15h,18h(quiz) | 21h(curiosidade)

---

## 🆘 **PROBLEMAS COMUNS**

### **Bot não responde:**
```bash
# Verificar se container está rodando
sudo docker ps

# Ver logs de erro
sudo docker-compose logs teacher-isa-bot

# Verificar arquivos de configuração
ls -la token.txt apikey.txt
```

### **Erro de memória:**
```bash
# Verificar RAM
free -h

# Se necessário, adicionar swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### **Erro de permissão:**
```bash
# Verificar se usuário está no grupo docker
groups $USER

# Se não estiver, adicionar e relogar
sudo usermod -aG docker $USER
exit
# Conectar novamente
```

---

## 🎯 **RESULTADO ESPERADO**

Após o deploy, você terá:

✅ **Teacher Isa Bot rodando 24/7** na Google Cloud  
✅ **Quiz interativos** com polls do Telegram  
✅ **IA conversacional** respondendo alunos  
✅ **Posts automáticos** nos horários certos  
✅ **Sistema robusto** com restart automático  
✅ **Monitoramento** em tempo real  

---

## 🚀 **PRÓXIMOS PASSOS OPCIONAIS**

### **Adicionar vídeos:**
```bash
# Criar pasta para vídeos
mkdir -p reels_content

# Upload vídeos (do seu Mac)
gcloud compute scp video*.mp4 SEU-USUARIO@SUA-VM:/home/SEU-USUARIO/teacher_isa_bot_deploy_*/reels_content/ --zone=SUA-ZONA

# Reiniciar bot para reconhecer vídeos
sudo docker-compose restart
```

### **Monitoramento avançado:**
```bash
# Configurar logs automáticos
sudo crontab -e
# Adicionar: 0 * * * * docker-compose -f /home/SEU-USUARIO/teacher_isa_bot_deploy_*/docker-compose.yml logs --tail=100 > /var/log/teacher_isa.log
```

---

**🎉 Seu Teacher Isa Bot está oficialmente na nuvem do Google! 🌐🎓**

**Para qualquer problema, verifique os logs primeiro:**
```bash
sudo docker-compose logs -f
```