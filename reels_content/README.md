# Como Adicionar Vídeos do @englishwithmrjay
## 📹 Guia para Postagens Automáticas

### 📁 Pasta de Vídeos
Esta pasta (`reels_content/`) é onde você deve colocar os vídeos que o bot postará automaticamente.

### 🎬 Como Baixar os Reels

#### Opção 1: Download Manual (Recomendado)
1. Acesse: https://www.instagram.com/englishwithmrjay/reels/
2. Use um site como:
   - https://saveinsta.app/
   - https://insta-downloader.com/
   - https://snapinsta.app/
3. Cole o link do reel que você quer
4. Baixe o vídeo
5. Coloque na pasta `reels_content/`

#### Opção 2: Apps Mobile
- **Android:** Video Downloader for Instagram
- **iOS:** Repost for Instagram

### 📂 Formatos Suportados
- `.mp4` (preferido)
- `.mov`
- `.avi` 
- `.mkv`

### 🕐 Como Funciona
- **09:00 da manhã**: Bot pega um vídeo aleatório da pasta
- **Comentário automático**: IA gera comentário educativo
- **Links**: Adiciona links para recursos premium
- **Hashtags**: Inclui hashtags relevantes

### 📝 Exemplo de Nomeação
```
reels_content/
├── grammar_tips_01.mp4
├── pronunciation_lesson_02.mp4
├── vocabulary_building_03.mp4
├── conversation_practice_04.mp4
└── business_english_05.mp4
```

### ⚠️ Importante
- **Direitos autorais**: Certifique-se de ter permissão para repostar
- **Qualidade**: Prefira vídeos em boa resolução
- **Tamanho**: Telegram aceita até 50MB por vídeo
- **Quantidade**: Adicione vários vídeos para variedade

### 🎯 Dica Pro
- Baixe 10-15 vídeos diferentes
- Bot selecionará aleatoriamente
- Evita repetição nos posts

### 🚀 Quando Estiver Pronto
Depois de adicionar os vídeos:
```bash
python teacher_isa_bot.py
```

O sistema automaticamente:
1. ✅ Detecta os vídeos na pasta
2. ✅ Posta às 9h da manhã
3. ✅ Gera comentários educativos
4. ✅ Adiciona call-to-action

**Boa sorte com o Teacher Isa Bot! 🎓📚**