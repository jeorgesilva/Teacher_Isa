#!/bin/bash
# 🌐 Script de Upload Rápido para Google Cloud VM
# ================================================

echo "🚀 Teacher Isa Bot - Upload para Google Cloud VM"
echo "================================================"

# Verificar se o pacote existe
if [ ! -d ~/Desktop/teacher_isa_bot_deploy_* ]; then
    echo "❌ Pacote de deploy não encontrado no Desktop!"
    echo "Execute primeiro o script download_for_cloud.sh"
    exit 1
fi

# Solicitar informações da VM
echo "📝 Configure sua VM do Google Cloud:"
read -p "🌐 IP externo da VM: " VM_IP
read -p "👤 Usuário da VM (geralmente seu email sem @gmail.com): " VM_USER
read -p "🔑 Zona da VM (ex: us-central1-a): " VM_ZONE
read -p "📛 Nome da VM: " VM_NAME

echo ""
echo "🔄 Configurações:"
echo "IP: $VM_IP"
echo "Usuário: $VM_USER"
echo "Zona: $VM_ZONE"
echo "Nome: $VM_NAME"
echo ""
read -p "Continuar? (y/N): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    echo "❌ Upload cancelado."
    exit 0
fi

# Encontrar o diretório mais recente
DEPLOY_DIR=$(ls -t ~/Desktop/teacher_isa_bot_deploy_* | head -1)
ZIP_FILE=$(ls -t ~/Desktop/teacher_isa_bot_deploy_*.zip | head -1)

echo "📦 Usando pacote: $DEPLOY_DIR"
echo "📦 Arquivo ZIP: $ZIP_FILE"

# Criar script de setup remoto
cat > /tmp/setup_bot.sh << 'EOF'
#!/bin/bash
echo "🔧 Configurando Teacher Isa Bot na VM..."

# Atualizar sistema
sudo apt update

# Instalar Docker se não estiver instalado
if ! command -v docker &> /dev/null; then
    echo "📦 Instalando Docker..."
    sudo apt install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "✅ Docker instalado!"
else
    echo "✅ Docker já instalado!"
fi

# Descompactar e preparar
if [ -f teacher_isa_bot_deploy_*.zip ]; then
    echo "📦 Descompactando pacote..."
    unzip -q teacher_isa_bot_deploy_*.zip
    cd teacher_isa_bot_deploy_*/
    
    # Dar permissões
    chmod +x deploy.sh monitor.sh
    
    echo "🚀 Executando deploy..."
    sudo ./deploy.sh
    
    echo "📊 Status final:"
    sudo docker-compose ps
    
    echo ""
    echo "✅ Deploy concluído!"
    echo "📱 Teste o bot no Telegram: /start"
    echo "🔍 Ver logs: sudo docker-compose logs -f"
    echo "📊 Monitorar: sudo ./monitor.sh"
else
    echo "❌ Arquivo ZIP não encontrado!"
fi
EOF

echo ""
echo "🚀 Iniciando upload e deploy..."

# Opção 1: Upload via SCP (se SSH estiver configurado)
echo "📤 Tentando upload via SCP..."
if scp "$ZIP_FILE" "/tmp/setup_bot.sh" "$VM_USER@$VM_IP:/home/$VM_USER/" 2>/dev/null; then
    echo "✅ Upload via SCP concluído!"
    
    echo "🔧 Executando setup remoto..."
    ssh "$VM_USER@$VM_IP" "bash setup_bot.sh"
    
    echo ""
    echo "🎉 Deploy concluído via SCP!"
    
else
    echo "⚠️ SCP falhou. Usando gcloud..."
    
    # Opção 2: Upload via gcloud
    echo "📤 Upload via gcloud compute scp..."
    
    # Upload do ZIP
    gcloud compute scp "$ZIP_FILE" "$VM_USER@$VM_NAME:/home/$VM_USER/" --zone="$VM_ZONE"
    
    # Upload do script de setup
    gcloud compute scp "/tmp/setup_bot.sh" "$VM_USER@$VM_NAME:/home/$VM_USER/" --zone="$VM_ZONE"
    
    # Executar setup
    echo "🔧 Executando setup remoto via gcloud..."
    gcloud compute ssh "$VM_USER@$VM_NAME" --zone="$VM_ZONE" --command="bash setup_bot.sh"
    
    echo ""
    echo "🎉 Deploy concluído via gcloud!"
fi

echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. 📱 Teste o bot: Envie /start para @teacher_isa_bot"
echo "2. 🔍 Ver logs: gcloud compute ssh $VM_USER@$VM_NAME --zone=$VM_ZONE --command='sudo docker-compose logs -f'"
echo "3. 📊 Monitorar: gcloud compute ssh $VM_USER@$VM_NAME --zone=$VM_ZONE --command='sudo ./monitor.sh'"
echo "4. 📹 Adicionar vídeos (opcional): Upload para pasta reels_content/"
echo ""
echo "🌐 Comandos úteis:"
echo "# Conectar à VM:"
echo "gcloud compute ssh $VM_USER@$VM_NAME --zone=$VM_ZONE"
echo ""
echo "# Status do bot:"
echo "gcloud compute ssh $VM_USER@$VM_NAME --zone=$VM_ZONE --command='sudo docker-compose ps'"
echo ""
echo "# Parar/iniciar bot:"
echo "gcloud compute ssh $VM_USER@$VM_NAME --zone=$VM_ZONE --command='sudo docker-compose down'"
echo "gcloud compute ssh $VM_USER@$VM_NAME --zone=$VM_ZONE --command='sudo docker-compose up -d'"
echo ""
echo "🎓 Teacher Isa Bot está rodando na Google Cloud! ✨"

# Limpar arquivo temporário
rm -f /tmp/setup_bot.sh

echo ""
echo "📊 Teste final: Envie uma mensagem para @teacher_isa_bot no Telegram!"
EOF