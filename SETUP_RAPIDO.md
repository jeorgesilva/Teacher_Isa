# 🚀 CONFIGURAÇÃO RÁPIDA - GOOGLE DRIVE

## ⚡ SETUP EM 5 MINUTOS

### 1️⃣ CRIAR SERVICE ACCOUNT (2 minutos)

1. **Acesse**: https://console.cloud.google.com/
2. **Crie um projeto novo** ou use existente
3. **Ative a Google Drive API**:
   - Menu: APIs & Services > Library
   - Procure: "Google Drive API"
   - Clique: "Enable"

4. **Crie Service Account**:
   - Menu: APIs & Services > Credentials
   - Clique: "Create Credentials" > "Service Account"
   - Nome: `teacher-isa-bot`
   - ID: `teacher-isa-bot`
   - Clique: "Create and Continue" > "Done"

### 2️⃣ BAIXAR CREDENCIAIS (1 minuto)

1. **Na lista de Service Accounts**, clique no que você criou
2. **Aba "Keys"** > "Add Key" > "Create new key"
3. **Formato**: JSON
4. **Baixe o arquivo**

### 3️⃣ INSTALAR NO BOT (30 segundos)

**Opção A - Arquivo Local** (Recomendado):
```bash
# Renomeie o arquivo baixado para:
google_credentials.json

# Coloque na pasta do bot:
/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/
```

**Opção B - Variável de Ambiente**:
```bash
export GOOGLE_DRIVE_CREDENTIALS='CONTEUDO_DO_ARQUIVO_JSON_AQUI'
```

### 4️⃣ COMPARTILHAR PASTA (1 minuto)

1. **Abra sua pasta**: https://drive.google.com/drive/folders/1KslzJkbExVY8X2ZifP6YGiM62BxNRSyc
2. **Clique em "Share"** (botão azul)
3. **Adicione o email do Service Account**:
   - Está no arquivo JSON: `"client_email": "teacher-isa-bot@SEU-PROJECT.iam.gserviceaccount.com"`
4. **Permissão**: "Viewer" (apenas visualizar)
5. **Clique**: "Send"

### 5️⃣ TESTAR (30 segundos)

```bash
# Verificar credenciais
python check_credentials.py

# Testar integração completa
python test_google_drive.py

# Executar bot
python teacher_isa_bot.py
```

---

## 🎯 EXEMPLO DO ARQUIVO JSON

Seu arquivo `google_credentials.json` deve parecer com isto:

```json
{
  "type": "service_account",
  "project_id": "seu-projeto-123456",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "teacher-isa-bot@seu-projeto-123456.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/teacher-isa-bot%40seu-projeto-123456.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

---

## ✅ VERIFICAÇÃO

Depois de configurar, execute:

```bash
python check_credentials.py
```

Deve mostrar:
```
✅ Arquivo válido!
📧 Service Account: teacher-isa-bot@seu-projeto.iam.gserviceaccount.com
```

---

## 🔧 COMANDOS ÚTEIS

```bash
# Verificar credenciais
python check_credentials.py

# Testar Google Drive
python test_google_drive.py

# Executar bot
python teacher_isa_bot.py

# No bot (admin commands):
/drive_test    # Testar download
/drive_sync    # Sincronizar vídeos  
/stats         # Ver estatísticas
```

---

## 🎬 COMO FUNCIONA

1. **Bot inicia** → Conecta com Google Drive
2. **9h da manhã** → Baixa vídeo aleatório da sua pasta
3. **Posta vídeo** → Com comentário educativo automático
4. **Cache local** → Evita downloads repetidos
5. **Você adiciona vídeos** → Bot detecta automaticamente

---

## ⚠️ DICAS IMPORTANTES

- ✅ **Compartilhe a pasta** com o email do Service Account
- ✅ **Permissão "Viewer"** é suficiente (segurança)
- ✅ **Formatos suportados**: MP4, MOV, AVI, MKV, WebM, 3GP
- ✅ **Adicione vídeos** quando quiser - bot detecta automaticamente
- ✅ **Cache inteligente** - economiza banda e espaço

---

**🚀 Pronto! Em 5 minutos seu bot estará usando vídeos do Google Drive!**