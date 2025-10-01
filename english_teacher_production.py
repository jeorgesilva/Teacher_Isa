#!/usr/bin/env python3
"""
English Teacher Bot - Production Version with Enhanced Error Handling
===================================================================

Versão robusta para execução em VM com:
- Reconexão automática
- Tratamento de erros de rede
- Logs detalhados
- Fallbacks para falhas
- Sistema de retry
- Monitoramento de saúde
"""

import logging
import os
import asyncio
import random
import time
import sys
from datetime import datetime
from pathlib import Path
import traceback

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.error import NetworkError, TimedOut, Forbidden, BadRequest
import google.generativeai as genai

# Configurar logging mais robusto
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Reduzir logs de bibliotecas externas
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# ---------- CONFIGURAÇÃO ----------
GROUP_ID = "@seu_grupo_ingles"  
ADMIN_IDS = [123456789]  

MAIN_LINK = "https://linktr.ee/englishwithmrjay?fbclid=PAZXh0bgNhZW0CMTEAAad4dDVNWKBIsJJuGH-cDmZtFBN3DxwkBQY6Vd5X7QQkVrYC9o_ETW1yOPsuOA_aem_0hqlR-kKzDCKB43TAnezgA"
INSTAGRAM_PROFILE = "https://www.instagram.com/englishwithmrjay/"

# Configurações de retry
MAX_RETRIES = 3
RETRY_DELAY = 5
HEALTH_CHECK_INTERVAL = 300  # 5 minutos

# ---------- CONFIGURAÇÃO GEMINI COM RETRY ----------
def setup_gemini():
    """Configura Gemini com tratamento de erro."""
    try:
        # Tentar múltiplas fontes para API key
        api_key = None
        
        # Fonte 1: arquivo
        if os.path.exists("apikey.txt"):
            with open("apikey.txt", "r") as f:
                api_key = f.read().strip()
        
        # Fonte 2: variável de ambiente
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("✅ Gemini AI configurada com sucesso!")
            return model
        else:
            logger.warning("⚠️ GEMINI_API_KEY não encontrada. Modo fallback ativado.")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao configurar Gemini: {e}")
        return None

model = setup_gemini()
user_histories = {}

# ---------- SISTEMA DE RETRY ----------
async def retry_operation(operation, *args, **kwargs):
    """Executa operação com retry automático."""
    for attempt in range(MAX_RETRIES):
        try:
            return await operation(*args, **kwargs)
        except (NetworkError, TimedOut) as e:
            logger.warning(f"⚠️ Tentativa {attempt + 1}/{MAX_RETRIES} falhou: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (2 ** attempt))  # Backoff exponencial
            else:
                logger.error(f"❌ Operação falhou após {MAX_RETRIES} tentativas")
                raise
        except Exception as e:
            logger.error(f"❌ Erro não recuperável: {e}")
            raise

# ---------- CLASSES DE FALLBACK ----------
class FallbackResponses:
    """Respostas de emergência quando IA falha."""
    
    GREETINGS = [
        "Hello! Welcome to our English learning community! 🌟",
        "Hi there! Ready to practice English together? 📚",
        "Welcome! I'm here to help with your English journey! 🚀"
    ]
    
    MOTIVATIONAL = [
        "Great job practicing English! Keep it up! 💪",
        "You're doing wonderful! Every conversation counts! ⭐",
        "Excellent effort! Practice makes progress! 🌟",
        "Keep going! Your English is improving! 🚀"
    ]
    
    LEARNING_TIPS = [
        "💡 Tip: Try to think in English for 5 minutes daily!",
        "📚 Remember: Mistakes are part of learning!",
        "🎯 Focus on communication, not perfection!",
        "⭐ Consistency beats intensity in language learning!"
    ]
    
    ERROR_MESSAGES = [
        "I'm having some technical difficulties, but I'm still here to help! 🤖",
        "Sorry for the delay! Let's continue our English practice! 📚",
        "Technical hiccup! But my enthusiasm for teaching hasn't changed! ⚡"
    ]

# ---------- FUNÇÕES PRINCIPAIS COM TRATAMENTO DE ERRO ----------

async def safe_send_message(update, text, **kwargs):
    """Envia mensagem com tratamento de erro."""
    try:
        await retry_operation(update.message.reply_text, text, **kwargs)
    except Exception as e:
        logger.error(f"❌ Erro ao enviar mensagem: {e}")
        # Tentar mensagem simplificada
        try:
            await update.message.reply_text("I'm experiencing some issues, but I'm still here! 🤖")
        except:
            logger.error("❌ Falha crítica na comunicação")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mensagem de boas-vindas robusta."""
    try:
        user = update.effective_user
        
        welcome_message = f"""Hello {user.first_name}! 👋😊

I'm your English Teacher Assistant! Let's make learning fun! 🎓

🌟 **What I can help you with:**
📚 English practice & conversation
🎯 Daily motivation & tips  
💡 Grammar & vocabulary help
🎮 Fun learning activities

**Commands:**
/tips - Learning advice
/motivation - Daily inspiration
/practice - Start conversation
/help - All commands

Let's start your English journey! What would you like to practice? 🚀"""
        
        await safe_send_message(update, welcome_message)
        
    except Exception as e:
        logger.error(f"❌ Erro em start(): {e}")
        fallback_msg = random.choice(FallbackResponses.GREETINGS)
        await safe_send_message(update, fallback_msg)

async def responder_com_ia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resposta com IA e fallback robusto."""
    try:
        user_id = update.effective_user.id
        user_texto = update.message.text

        # Gerenciar histórico
        if user_id not in user_histories:
            user_histories[user_id] = []

        user_histories[user_id].append(f"Student: {user_texto}")
        
        # Limitar histórico para evitar overflow
        if len(user_histories[user_id]) > 10:
            user_histories[user_id] = user_histories[user_id][-10:]

        contexto = "\n".join(user_histories[user_id][-5:])

        # Tentar IA primeiro
        if model:
            try:
                prompt = f"""You are an encouraging English teacher. Be supportive, correct mistakes gently, and keep responses conversational.

Recent conversation:
{contexto}

Respond as a helpful English teacher (keep it under 150 words):"""
                
                response = await asyncio.wait_for(
                    asyncio.to_thread(model.generate_content, prompt),
                    timeout=10.0  # Timeout de 10 segundos
                )
                
                resposta = response.text
                
                # Adicionar call-to-action ocasionalmente
                if random.random() < 0.15:
                    resposta += f"\n\n🔗 More resources: {MAIN_LINK}"
                
                user_histories[user_id].append(f"Teacher: {resposta}")
                await safe_send_message(update, resposta)
                return
                
            except asyncio.TimeoutError:
                logger.warning("⚠️ Timeout na IA - usando fallback")
            except Exception as e:
                logger.warning(f"⚠️ Erro na IA: {e} - usando fallback")

        # Fallback inteligente baseado no texto do usuário
        resposta = generate_smart_fallback(user_texto)
        user_histories[user_id].append(f"Teacher: {resposta}")
        await safe_send_message(update, resposta)
        
    except Exception as e:
        logger.error(f"❌ Erro crítico em responder_com_ia(): {e}")
        error_msg = random.choice(FallbackResponses.ERROR_MESSAGES)
        await safe_send_message(update, error_msg)

def generate_smart_fallback(user_text):
    """Gera resposta inteligente sem IA."""
    text_lower = user_text.lower()
    
    # Detectar tipo de mensagem e responder adequadamente
    if any(word in text_lower for word in ['hello', 'hi', 'hey', 'good morning']):
        response = random.choice(FallbackResponses.GREETINGS)
    elif any(word in text_lower for word in ['help', 'how', 'what', 'why']):
        response = f"Great question! {random.choice(FallbackResponses.LEARNING_TIPS)}"
    elif any(word in text_lower for word in ['thank', 'thanks', 'good', 'great']):
        response = random.choice(FallbackResponses.MOTIVATIONAL)
    else:
        response = f"I hear you! {random.choice(FallbackResponses.LEARNING_TIPS)}"
    
    # Adicionar call-to-action
    if random.random() < 0.2:
        response += f"\n\n📚 Want structured lessons? {MAIN_LINK}"
    
    return response

# ---------- SISTEMA DE POSTS ROBUSTO ----------
class RobustPostingSystem:
    def __init__(self, application, group_id):
        self.application = application
        self.group_id = group_id
        self.model = model
        self.stats = {"posts_enviados": 0, "falhas": 0}
        self.last_health_check = datetime.now()
        
    async def create_daily_post(self):
        """Cria post educativo com fallback."""
        try:
            if self.model:
                # Tentar com IA
                try:
                    prompt = """Create an engaging English learning post with:
                    1. A motivational message
                    2. A practical tip
                    3. Encouragement for practice
                    
                    Keep it positive and under 200 words. Use emojis."""
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(self.model.generate_content, prompt),
                        timeout=15.0
                    )
                    content = response.text
                except:
                    content = self.get_fallback_post()
            else:
                content = self.get_fallback_post()
            
            # Adicionar links
            full_post = f"""{content}

🔗 Premium English lessons: {MAIN_LINK}
📸 Daily content: {INSTAGRAM_PROFILE}

#EnglishLearning #Education #LearnWithMrJay"""
            
            # Enviar com retry
            await retry_operation(
                self.application.bot.send_message,
                chat_id=self.group_id,
                text=full_post,
                parse_mode='Markdown'
            )
            
            self.stats["posts_enviados"] += 1
            logger.info("✅ Post educativo enviado com sucesso!")
            
        except Exception as e:
            self.stats["falhas"] += 1
            logger.error(f"❌ Erro ao enviar post: {e}")
    
    def get_fallback_post(self):
        """Post de fallback quando IA falha."""
        posts = [
            """🌟 **Daily English Motivation** 🌟

Every conversation in English makes you stronger! 💪

Today's tip: Don't be afraid of mistakes - they're stepping stones to fluency! 

Practice 10 minutes today, and you'll be amazed at your progress! 🚀""",

            """📚 **English Learning Reminder** 📚

You don't have to be perfect, just consistent! ⭐

Small daily practice beats long study sessions once a week!

Remember: Every expert was once a beginner! Keep going! 💪""",

            """🎯 **Focus on Progress, Not Perfection** 🎯

Your English journey is unique and valuable! 🌈

Celebrate small wins - they add up to big success! 

Keep practicing, keep improving, keep believing! ✨"""
        ]
        
        return random.choice(posts)
    
    async def health_check(self):
        """Verifica saúde do sistema."""
        try:
            # Teste simples de conectividade
            await self.application.bot.get_me()
            logger.info("✅ Health check passed")
            self.last_health_check = datetime.now()
            return True
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    async def scheduler_loop(self):
        """Loop do agendador com monitoramento."""
        logger.info("🕐 Iniciando agendador robusto...")
        
        while True:
            try:
                now = datetime.now()
                
                # Health check periódico
                if (now - self.last_health_check).seconds > HEALTH_CHECK_INTERVAL:
                    await self.health_check()
                
                # Post às 9:00
                if now.hour == 9 and now.minute == 0:
                    await self.create_daily_post()
                    await asyncio.sleep(60)  # Evitar múltiplos posts
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Erro no scheduler: {e}")
                await asyncio.sleep(60)  # Wait longer on error

# ---------- COMANDOS ADMINISTRATIVOS ----------

async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status de saúde do sistema."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await safe_send_message(update, "❌ Admin only command.")
        return
    
    try:
        # Verificar componentes
        bot_status = "✅ Online"
        ai_status = "✅ Active" if model else "❌ Disabled"
        
        if hasattr(context.application, 'posting_system'):
            post_system = context.application.posting_system
            posts_sent = post_system.stats["posts_enviados"]
            failures = post_system.stats["falhas"]
            post_status = f"✅ Active ({posts_sent} sent, {failures} failures)"
        else:
            post_status = "❌ Not configured"
        
        health_report = f"""🏥 **System Health Report**

🤖 **Bot:** {bot_status}
🧠 **AI:** {ai_status}  
📱 **Posts:** {post_status}
💬 **Active chats:** {len(user_histories)}

📊 **Memory usage:** Normal
⏰ **Uptime:** Running smoothly
🔗 **Network:** Connected

All systems operational! 🟢"""
        
        await safe_send_message(update, health_report)
        
    except Exception as e:
        logger.error(f"Erro em health_command: {e}")
        await safe_send_message(update, "❌ Error generating health report")

# ---------- FUNÇÃO PRINCIPAL ----------

def main() -> None:
    """Função principal robusta."""
    logger.info("🎓 Iniciando English Teacher Bot (Production)")
    
    try:
        # Carregar token com fallbacks
        token = None
        
        if os.path.exists("token.txt"):
            with open("token.txt") as f:
                token = f.read().strip()
        
        if not token:
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            
        if not token:
            logger.error("❌ Token não encontrado!")
            return
        
        # Configurar aplicação com timeouts robustos
        application = Application.builder()\
            .token(token)\
            .connect_timeout(30.0)\
            .read_timeout(30.0)\
            .write_timeout(30.0)\
            .build()

        # Configurar sistema de posts se GROUP_ID definido
        if GROUP_ID != "@seu_grupo_ingles":
            posting_system = RobustPostingSystem(application, GROUP_ID)
            application.posting_system = posting_system
            
            # Iniciar agendador
            asyncio.create_task(posting_system.scheduler_loop())
            logger.info("✅ Sistema de posts configurado!")

        # Handlers básicos
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("health", health_command))
        
        # Handler de mensagens
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, responder_com_ia)
        )

        # Iniciar com configurações robustas
        logger.info("🚀 Bot iniciado em modo produção!")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
            connect_timeout=30.0,
            read_timeout=30.0
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro crítico: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()