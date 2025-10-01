"""
CONFIGURAÇÃO DO GOOGLE DRIVE para Teacher Isa Bot
==============================================

📋 PASSOS PARA CONFIGURAR GOOGLE DRIVE API:

1. 🔧 CRIAR PROJETO NO GOOGLE CLOUD CONSOLE:
   - Acesse: https://console.cloud.google.com/
   - Crie um novo projeto ou use existente
   - Anote o Project ID

2. ⚙️ ATIVAR API DO GOOGLE DRIVE:
   - Vá em "APIs & Services" > "Library"
   - Procure por "Google Drive API"
   - Clique em "Enable"

3. 🔑 CRIAR SERVICE ACCOUNT:
   - Vá em "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "Service Account"
   - Preencha os dados:
     * Nome: teacher-isa-drive-access
     * ID: teacher-isa-drive
     * Descrição: Acesso aos vídeos do Google Drive
   - Clique em "Create and Continue"
   - Pule as permissões opcionais
   - Clique em "Done"

4. 📁 BAIXAR CHAVE JSON:
   - Na lista de Service Accounts, clique no que você criou
   - Vá na aba "Keys"
   - Clique em "Add Key" > "Create new key"
   - Escolha formato "JSON"
   - Baixe o arquivo

5. 🔗 COMPARTILHAR PASTA DO GOOGLE DRIVE:
   - Abra sua pasta de vídeos: https://drive.google.com/drive/folders/1KslzJkbExVY8X2ZifP6YGiM62BxNRSyc
   - Clique em "Share" (Compartilhar)
   - Adicione o email do Service Account encontrado no arquivo JSON
   - O email é algo como: teacher-isa-drive@seu-projeto.iam.gserviceaccount.com
   - Dê permissão "Viewer" (apenas visualizar)
   - Clique em "Send"

6. 💾 INSTALAR CREDENCIAIS NO BOT:
   
   OPÇÃO A - Arquivo local:
   - Renomeie o arquivo baixado para: google_credentials.json
   - Coloque na mesma pasta do teacher_isa_bot.py

   OPÇÃO B - Variável de ambiente:
   - Abra o arquivo JSON baixado
   - Copie todo o conteúdo
   - Defina variável de ambiente:
     export GOOGLE_DRIVE_CREDENTIALS='{"type": "service_account", ...}'

7. ✅ TESTAR CONEXÃO:
   - Execute o bot
   - Use comando /drive_test (admin only)
   - Deve mostrar vídeos encontrados na pasta

📝 FORMATOS DE VÍDEO SUPORTADOS:
- MP4 (.mp4)
- QuickTime (.mov)
- AVI (.avi)
- Matroska (.mkv)
- WebM (.webm)
- 3GP (.3gp)

🎯 COMO FUNCIONA:
1. Bot sincroniza lista de vídeos da pasta periodicamente
2. Quando precisa postar vídeo, baixa um aleatório para cache local
3. Cache é gerenciado automaticamente (limite de 200MB)
4. Fallback para pasta local se Google Drive falhar

🔧 COMANDOS ADMINISTRATIVOS:
/drive_sync - Forçar sincronização de vídeos
/drive_test - Testar download de vídeo
/drive_cache - Limpar cache local
/stats - Ver estatísticas incluindo Google Drive

⚠️ DICAS IMPORTANTES:
- Service Account é mais seguro que OAuth para bots
- Mantenha as credenciais seguras e privadas
- Pasta deve estar compartilhada com o Service Account
- Bot baixa vídeos sob demanda para economizar espaço
- Cache local evita downloads repetidos

🔄 ATUALIZAÇÃO DINÂMICA:
- Adicione novos vídeos na pasta do Google Drive
- Bot detectará automaticamente na próxima sincronização
- Não precisa reiniciar o bot

📊 MONITORAMENTO:
- Use /stats para ver status da conexão
- Use /health para verificar funcionamento
- Logs mostram detalhes de downloads e erros