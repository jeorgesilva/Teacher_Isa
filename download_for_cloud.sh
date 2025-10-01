#!/bin/bash
# 📦 Teacher Isa Bot - Download Script para Deploy na Nuvem
# ========================================================

echo "🎓 Teacher Isa Bot - Preparando para Deploy na Nuvem"
echo "===================================================="

# Definir variáveis
PROJECT_NAME="teacher_isa_bot"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${HOME}/Desktop/${PROJECT_NAME}_deploy_${TIMESTAMP}"

echo "📁 Criando diretório de deploy: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Copiar arquivos principais
echo "📋 Copiando arquivos do projeto..."

# Arquivo principal do bot
cp "/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/teacher_isa_bot.py" "$BACKUP_DIR/"

# Arquivos de configuração
cp "/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/token.txt" "$BACKUP_DIR/"
cp "/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/apikey.txt" "$BACKUP_DIR/"

# Criar requirements.txt
echo "📝 Criando requirements.txt..."
cat > "$BACKUP_DIR/requirements.txt" << EOF
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
echo "🐳 Criando Dockerfile..."
cat > "$BACKUP_DIR/Dockerfile" << EOF
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar arquivos do projeto
COPY teacher_isa_bot.py .
COPY token.txt .
COPY apikey.txt .

# Criar diretório para vídeos
RUN mkdir -p reels_content

# Comando para executar o bot
CMD ["python", "teacher_isa_bot.py"]
EOF

# Criar docker-compose.yml
echo "🔧 Criando docker-compose.yml..."
cat > "$BACKUP_DIR/docker-compose.yml" << EOF
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

volumes:
  bot_logs:
EOF

# Criar script de deploy
echo "🚀 Criando script de deploy..."
cat > "$BACKUP_DIR/deploy.sh" << 'EOF'
#!/bin/bash
# 🚀 Deploy Script para Teacher Isa Bot

echo "🎓 Iniciando deploy do Teacher Isa Bot..."

# Parar containers existentes
echo "⏹️ Parando containers existentes..."
docker-compose down

# Rebuild e start
echo "🔨 Construindo e iniciando container..."
docker-compose up --build -d

echo "✅ Deploy concluído!"
echo "📊 Para ver logs: docker-compose logs -f"
echo "🔍 Para status: docker-compose ps"
EOF

chmod +x "$BACKUP_DIR/deploy.sh"

# Criar script de monitoramento
echo "📊 Criando script de monitoramento..."
cat > "$BACKUP_DIR/monitor.sh" << 'EOF'
#!/bin/bash
# 📊 Monitor Script para Teacher Isa Bot

echo "🏥 Teacher Isa Bot - Status do Sistema"
echo "===================================="

# Status do container
echo "🐳 Status do Container:"
docker-compose ps

echo ""
echo "📊 Logs recentes:"
docker-compose logs --tail=20

echo ""
echo "💾 Uso de recursos:"
docker stats teacher_isa_bot --no-stream

echo ""
echo "📁 Arquivos de vídeo:"
ls -la reels_content/ || echo "Pasta reels_content não encontrada"
EOF

chmod +x "$BACKUP_DIR/monitor.sh"

# Criar README para deploy
echo "📖 Criando README.md..."
cat > "$BACKUP_DIR/README.md" << 'EOF'
# 🎓 Teacher Isa Bot - Deploy Package

Este pacote contém todos os arquivos necessários para fazer deploy do Teacher Isa Bot na nuvem.

## 📦 Conteúdo do Pacote

- `teacher_isa_bot.py` - Código principal do bot
- `token.txt` - Token do bot do Telegram
- `apikey.txt` - Chave da API do Gemini
- `requirements.txt` - Dependências Python
- `Dockerfile` - Configuração do container
- `docker-compose.yml` - Orquestração de containers
- `deploy.sh` - Script de deploy automatizado
- `monitor.sh` - Script de monitoramento

## 🚀 Como Fazer Deploy

### 1. **Upload para Servidor**
```bash
# Fazer upload de todos os arquivos para seu servidor na nuvem
scp -r teacher_isa_bot_deploy_* user@your-server:/home/user/
```

### 2. **Conectar ao Servidor**
```bash
ssh user@your-server
cd teacher_isa_bot_deploy_*
```

### 3. **Executar Deploy**
```bash
# Dar permissão de execução
chmod +x deploy.sh monitor.sh

# Executar deploy
./deploy.sh
```

### 4. **Monitorar**
```bash
# Ver status
./monitor.sh

# Logs em tempo real
docker-compose logs -f
```

## 📹 Adicionar Vídeos

1. Criar pasta `reels_content/` no servidor
2. Fazer upload dos vídeos do @englishwithmrjay
3. Formatos suportados: .mp4, .mov, .avi, .mkv

```bash
mkdir -p reels_content
# Upload dos vídeos para reels_content/
```

## 🔧 Comandos Úteis

### Gerenciamento do Container
```bash
# Parar bot
docker-compose down

# Iniciar bot
docker-compose up -d

# Reiniciar bot
docker-compose restart

# Ver logs
docker-compose logs -f

# Status
docker-compose ps
```

### Monitoramento
```bash
# Status do sistema
./monitor.sh

# Estatísticas de CPU/RAM
docker stats teacher_isa_bot

# Espaço em disco
df -h
```

## 🌐 Providers de Nuvem Recomendados

### DigitalOcean
- **Droplet**: Ubuntu 22.04, 1GB RAM, $6/mês
- **Setup**: Docker pré-instalado disponível

### AWS EC2
- **Instance**: t3.micro (Free Tier), Ubuntu 22.04
- **Setup**: Instalar Docker manualmente

### Google Cloud Platform
- **VM**: e2-micro (Free Tier), Ubuntu 22.04
- **Setup**: Marketplace com Docker

### Vultr
- **Instance**: Regular Performance, 1GB RAM, $6/mês
- **Setup**: Docker application available

## 🔐 Configuração de Segurança

### Firewall
```bash
# Permitir apenas SSH e saída
ufw allow ssh
ufw enable
```

### Updates Automáticos
```bash
# Configurar updates automáticos
apt update && apt upgrade -y
apt install unattended-upgrades -y
```

## 📊 Horários de Postagem

- **09:00** - Vídeo diário
- **12:00** - Quiz 1
- **15:00** - Quiz 2  
- **18:00** - Quiz 3
- **21:00** - Curiosidade sobre inglês

## 🛠️ Troubleshooting

### Bot não inicia
```bash
# Verificar logs
docker-compose logs teacher-isa-bot

# Verificar arquivos
ls -la token.txt apikey.txt
```

### Erro de memória
```bash
# Aumentar swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Container para sozinho
```bash
# Verificar recursos
docker stats
free -h
df -h

# Reiniciar
docker-compose restart
```

## 📱 Configuração Final

1. **Grupo/Canal**: Configurado para `@English_teacher`
2. **Admins**: IDs configurados no código
3. **IA**: Gemini 2.5 Flash ativa
4. **Polls**: Quiz interativos funcionando

**🎉 Seu Teacher Isa Bot está pronto para ensinar inglês 24/7 na nuvem!**
EOF

# Criar pasta para vídeos
mkdir -p "$BACKUP_DIR/reels_content"

# Copiar documentação adicional se existir
if [ -f "/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/STATUS.md" ]; then
    cp "/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/STATUS.md" "$BACKUP_DIR/"
fi

if [ -f "/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/QUIZ_POLLS_UPDATE.md" ]; then
    cp "/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/QUIZ_POLLS_UPDATE.md" "$BACKUP_DIR/"
fi

if [ -f "/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/FIXES_APPLIED.md" ]; then
    cp "/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/FIXES_APPLIED.md" "$BACKUP_DIR/"
fi

# Criar arquivo de informações do deploy
echo "ℹ️ Criando informações do deploy..."
cat > "$BACKUP_DIR/DEPLOY_INFO.txt" << EOF
🎓 Teacher Isa Bot - Informações do Deploy
========================================

📅 Data de criação: $(date)
🖥️ Sistema origem: $(uname -s)
👤 Usuário: $(whoami)
📁 Diretório: $BACKUP_DIR

📋 Arquivos incluídos:
- teacher_isa_bot.py (Código principal)
- token.txt (Token do bot)
- apikey.txt (Chave Gemini)
- requirements.txt (Dependências)
- Dockerfile (Container)
- docker-compose.yml (Orquestração)
- deploy.sh (Script de deploy)
- monitor.sh (Monitoramento)
- README.md (Documentação completa)

🎯 Configurações atuais:
- Grupo: @English_teacher
- Bot: @teacher_isa_bot
- IA: Gemini 2.5 Flash
- Horários: 9h(vídeo) | 12h,15h,18h(quiz) | 21h(curiosidade)

🚀 Para fazer deploy:
1. Upload para servidor na nuvem
2. Executar: chmod +x deploy.sh && ./deploy.sh
3. Monitorar: ./monitor.sh

✅ Pronto para produção!
EOF

echo "✅ Deploy package criado com sucesso!"
echo "📁 Localização: $BACKUP_DIR"
echo ""
echo "📋 Arquivos criados:"
ls -la "$BACKUP_DIR"
echo ""
echo "🚀 Próximos passos:"
echo "1. Fazer upload da pasta para seu servidor na nuvem"
echo "2. Executar: chmod +x deploy.sh && ./deploy.sh"
echo "3. Monitorar: ./monitor.sh"
echo ""
echo "🎓 Seu Teacher Isa Bot está pronto para a nuvem!"
EOF