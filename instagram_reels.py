#!/usr/bin/env python3
"""
Instagram Reels Integration for English Teacher Bot
=================================================

Este sistema baixa e posta reels do @englishwithmrjay automaticamente.
Funciona como complemento ao bot principal.

NOTA: Para usar este sistema, você precisará:
1. Instalar yt-dlp: pip install yt-dlp
2. Configurar acesso aos reels (pode precisar de autenticação)
3. Respeitar os termos de uso do Instagram

ALTERNATIVA RECOMENDADA:
- Baixar manualmente os reels do @englishwithmrjay
- Salvar na pasta 'reels_content'
- O bot postará automaticamente com comentários educativos
"""

import os
import random
import asyncio
import logging
from pathlib import Path
from datetime import datetime, time

logger = logging.getLogger(__name__)

class InstagramReelsManager:
    def __init__(self, application, group_id, model):
        self.application = application
        self.group_id = group_id
        self.model = model
        self.reels_folder = Path("reels_content")
        self.reels_folder.mkdir(exist_ok=True)
        
    def get_available_reels(self):
        """Lista reels disponíveis na pasta."""
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
        reels = []
        
        for ext in video_extensions:
            reels.extend(self.reels_folder.glob(f"*{ext}"))
        
        return list(reels)
    
    async def create_educational_comment(self):
        """Cria comentário educativo para o reel."""
        
        if not self.model:
            # Comentários pré-definidos como fallback
            comments = [
                """🎬 Amazing English lesson from @englishwithmrjay! 

This is exactly what makes learning fun and effective! 📚✨

Key takeaway: Practice daily, even if it's just for 5 minutes! 

Ready to take your English to the next level? 👇""",
                
                """🌟 Love this teaching style! 

Mr. Jay makes English so accessible and fun! This is how language learning should be! 💪

Remember: Every expert was once a beginner! 

Want more structured lessons like this? 👇""",
                
                """📚 Perfect example of practical English! 

This is why we follow @englishwithmrjay - real English for real situations! 🎯

Pro tip: Save this video and practice along! 

Ready for personalized English coaching? 👇"""
            ]
            
            return random.choice(comments)
        
        else:
            try:
                prompt = """Create an engaging educational comment for an English learning reel from @englishwithmrjay.

The comment should:
1. Praise the teaching method
2. Highlight a key learning point
3. Motivate viewers to practice
4. Be enthusiastic and supportive

Keep it professional, educational, and encouraging. Use emojis appropriately.
Don't include links - they will be added separately.
"""
                
                response = self.model.generate_content(prompt)
                return response.text
                
            except Exception as e:
                logger.error(f"Erro ao gerar comentário: {e}")
                return await self.create_educational_comment()  # Fallback
    
    async def post_reel_with_comment(self):
        """Posta um reel com comentário educativo."""
        
        available_reels = self.get_available_reels()
        
        if not available_reels:
            logger.warning("❌ Nenhum reel encontrado na pasta reels_content!")
            
            # Enviar post texto apenas
            await self.post_text_only()
            return
        
        # Selecionar reel aleatório
        selected_reel = random.choice(available_reels)
        
        # Criar comentário educativo
        comment = await self.create_educational_comment()
        
        # Link educacional
        main_link = "https://linktr.ee/englishwithmrjay?fbclid=PAZXh0bgNhZW0CMTEAAad4dDVNWKBIsJJuGH-cDmZtFBN3DxwkBQY6Vd5X7QQkVrYC9o_ETW1yOPsuOA_aem_0hqlR-kKzDCKB43TAnezgA"
        instagram_link = "https://www.instagram.com/englishwithmrjay/"
        
        full_caption = f"""{comment}

🔗 Get personalized English lessons: {main_link}

📸 Follow for daily content: {instagram_link}

#EnglishLearning #LearnWithMrJay #EnglishTips #Education"""
        
        try:
            # Enviar vídeo com caption
            with open(selected_reel, 'rb') as video_file:
                await self.application.bot.send_video(
                    chat_id=self.group_id,
                    video=video_file,
                    caption=full_caption,
                    parse_mode='Markdown'
                )
            
            logger.info(f"✅ Reel postado: {selected_reel.name}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao postar reel: {e}")
            # Fallback para post texto
            await self.post_text_only()
    
    async def post_text_only(self):
        """Post educativo apenas texto (fallback)."""
        
        comment = await self.create_educational_comment()
        main_link = "https://linktr.ee/englishwithmrjay?fbclid=PAZXh0bgNhZW0CMTEAAad4dDVNWKBIsJJuGH-cDmZtFBN3DxwkBQY6Vd5X7QQkVrYC9o_ETW1yOPsuOA_aem_0hqlR-kKzDCKB43TAnezgA"
        instagram_link = "https://www.instagram.com/englishwithmrjay/"
        
        full_message = f"""{comment}

🔗 Access premium English content: {main_link}

📸 Daily English tips: {instagram_link}

#EnglishLearning #Motivation #KeepLearning"""
        
        try:
            await self.application.bot.send_message(
                chat_id=self.group_id,
                text=full_message,
                parse_mode='Markdown'
            )
            
            logger.info("✅ Post educativo enviado (texto)")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar post: {e}")

# Função para integrar com o bot principal
def setup_reels_integration(application, group_id, model):
    """Configura integração com reels do Instagram."""
    reels_manager = InstagramReelsManager(application, group_id, model)
    application.reels_manager = reels_manager
    return reels_manager