#!/usr/bin/env python3
"""
English Teacher Bot - Mrs. Jay's Teaching Assistant
================================================

Um bot educativo que ajuda estudantes de inglês com:
1. Conversas educativas e motivadoras
2. Posts diários com reels do @englishwithmrjay 
3. Dicas de inglês e motivação
4. Call-to-action para aulas e recursos

Personalidade: Professora divertida, motivadora e paciente
"""

import logging
import os
import asyncio
import random
from datetime import datetime, time
from pathlib import Path

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# ---------- CONFIGURAÇÃO ----------
# IMPORTANTE: Configure estas variáveis!

GROUP_ID = "@seu_grupo_ingles"  # ou ID numérico do grupo/canal
ADMIN_IDS = [123456789]  # Adicione seu ID aqui

# Links educacionais
MAIN_LINK = "https://linktr.ee/englishwithmrjay?fbclid=PAZXh0bgNhZW0CMTEAAad4dDVNWKBIsJJuGH-cDmZtFBN3DxwkBQY6Vd5X7QQkVrYC9o_ETW1yOPsuOA_aem_0hqlR-kKzDCKB43TAnezgA"
INSTAGRAM_PROFILE = "https://www.instagram.com/englishwithmrjay/"

# ---------- CONFIGURAÇÃO GEMINI ----------
GEMINI_API_KEY = None

try:
    with open("apikey.txt", "r") as f:
        GEMINI_API_KEY = f.read().strip()
except FileNotFoundError:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    logger.info("Gemini AI configurada com sucesso! (modelo: gemini-2.5-flash)")
else:
    model = None
    logger.warning("GEMINI_API_KEY não encontrada. Funcionalidades de IA desabilitadas.")

# Memória das conversas
user_histories = {}

# ---------- FRASES MOTIVACIONAIS ----------
MOTIVATIONAL_PHRASES = [
    "Every expert was once a beginner! 🌟",
    "Practice makes progress, not perfection! 💪",
    "You're doing amazing! Keep going! 🚀",
    "English is your key to the world! 🗝️🌍",
    "Small steps daily = Big results! 📈",
    "Mistakes are proof you're trying! ✨",
    "You've got this, English learner! 🎯",
    "Learning never stops, and neither should you! 📚",
    "Your English journey is unique and beautiful! 🌈",
    "Today's effort is tomorrow's fluency! ⭐"
]

CALL_TO_ACTIONS = [
    "Ready to level up your English? Check out our amazing resources! 📚✨",
    "Want personalized English lessons? Let's make it happen! 🎯",
    "Join thousands of successful English learners! 🌟",
    "Transform your English skills today! 🚀",
    "Get exclusive access to premium English content! 💎",
    "Start your English fluency journey now! 🗣️",
    "Unlock your English potential! 🔓",
    "Professional English coaching awaits you! 👨‍🏫"
]

# ---------- FUNÇÕES DE CONVERSAÇÃO ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mensagem de apresentação da professora."""
    user = update.effective_user
    
    welcome_message = f"""Hello there, {user.first_name}! 👋😊

I'm Mrs. Jay's Teaching Assistant! I'm here to help you on your English learning journey! 🎓📚

🌟 **What I can do for you:**

📚 **English Practice** - Chat with me to improve your skills!
🎯 **Daily Motivation** - Get inspired to keep learning
🎬 **Educational Content** - Daily posts with amazing English tips
💡 **Learning Tips** - Practical advice for faster progress
🎮 **Fun Activities** - Interactive English games and exercises

**How to use me:**
• Just chat with me in English (I'll help if you make mistakes!) 💬
• Type /tips for learning advice 📝
• /motivation for daily inspiration ⭐
• /resources to access premium content 🎯
• /help to see all commands 🔧

Remember: Every conversation is practice! Don't worry about making mistakes - that's how we learn! 💪✨

What would you like to practice today? 🚀"""
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comandos disponíveis."""
    user_id = update.effective_user.id
    is_admin = user_id in ADMIN_IDS
    
    base_commands = """📚 **Available Commands:**

🎯 **For Students:**
/tips - Get practical English learning tips
/motivation - Daily motivation boost
/resources - Access premium learning materials
/grammar - Quick grammar help
/vocabulary - Learn new words daily
/practice - Start a conversation practice

💬 **Practice Mode:**
Just talk to me! I'll help you improve naturally while we chat! 🗣️

✨ Remember: The best way to learn English is to USE it! So let's chat! 💪"""

    admin_commands = """

🔧 **Admin Commands:**
/post_now - Send educational post now
/stats - View bot statistics
/status - Check system status"""

    answer = base_commands + (admin_commands if is_admin else "")
    await update.message.reply_text(answer)

async def tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dicas de aprendizado."""
    tips = [
        "🎯 **Tip 1:** Watch English content with subtitles, then without!",
        "📚 **Tip 2:** Learn 5 new words daily and use them in sentences!",
        "🗣️ **Tip 3:** Speak to yourself in English for 10 minutes daily!",
        "📝 **Tip 4:** Keep an English diary - write about your day!",
        "🎵 **Tip 5:** Listen to English songs and try to understand the lyrics!",
        "👥 **Tip 6:** Find English-speaking friends online to practice with!",
        "📱 **Tip 7:** Change your phone language to English!",
        "🎬 **Tip 8:** Watch your favorite movies in English!",
        "📖 **Tip 9:** Read English news for 15 minutes daily!",
        "🎲 **Tip 10:** Play word games in English to expand vocabulary!"
    ]
    
    tip = random.choice(tips)
    motivational = random.choice(MOTIVATIONAL_PHRASES)
    
    response = f"""{tip}

{motivational}

Want more personalized tips and structured lessons? 👇
{MAIN_LINK}"""
    
    await update.message.reply_text(response)

async def motivation_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mensagem motivacional."""
    motivational = random.choice(MOTIVATIONAL_PHRASES)
    call_to_action = random.choice(CALL_TO_ACTIONS)
    
    response = f"""🌟 **Daily Motivation** 🌟

{motivational}

Remember: Learning English is like building a house - brick by brick, day by day! 🏗️

You don't have to be perfect, you just have to be consistent! Every conversation, every mistake, every "aha!" moment is progress! 💪

{call_to_action} 👇
{MAIN_LINK}

Keep shining, English star! ⭐✨"""
    
    await update.message.reply_text(response)

async def resources_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recursos de aprendizado."""
    response = f"""📚 **Premium English Resources** 📚

🎯 **What you'll find:**
• Structured lesson plans 📝
• Interactive exercises 🎮
• Grammar explanations 📖
• Vocabulary builders 💡
• Speaking practice sessions 🗣️
• Pronunciation guides 🔊

👨‍🏫 **With Mr. Jay, you get:**
✅ Personalized learning path
✅ Real-time feedback
✅ Community support
✅ Progress tracking
✅ Flexible scheduling

🚀 **Ready to accelerate your English?**
Access all premium content here: 👇
{MAIN_LINK}

Follow our daily tips on Instagram: 📸
{INSTAGRAM_PROFILE}

Your fluency journey starts with one click! 🌟"""
    
    await update.message.reply_text(response)

async def grammar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ajuda com gramática."""
    grammar_tips = [
        "📝 **Present Simple vs Present Continuous:**\n'I work' (routine) vs 'I am working' (now)",
        "🔤 **Articles:** Use 'a/an' for general things, 'the' for specific things",
        "⏰ **Past Tense:** Regular verbs add '-ed', irregular verbs are special!",
        "❓ **Questions:** Remember to use 'do/does/did' for questions!",
        "🔄 **Prepositions:** IN (months/years), ON (days/dates), AT (times)",
    ]
    
    tip = random.choice(grammar_tips)
    
    response = f"""{tip}

Need more detailed grammar help? Our structured courses cover everything! 📚✨

{MAIN_LINK}"""
    
    await update.message.reply_text(response)

async def vocabulary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Palavras do dia."""
    vocab_sets = [
        {
            "theme": "Daily Routine 🌅",
            "words": ["wake up", "brush teeth", "have breakfast", "commute", "take a break"]
        },
        {
            "theme": "Emotions 😊",
            "words": ["excited", "anxious", "grateful", "overwhelmed", "confident"]
        },
        {
            "theme": "Business 💼",
            "words": ["deadline", "meeting", "presentation", "colleague", "project"]
        },
        {
            "theme": "Technology 💻",
            "words": ["download", "update", "wireless", "software", "backup"]
        }
    ]
    
    vocab_set = random.choice(vocab_sets)
    
    response = f"""📚 **Vocabulary of the Day** 📚

🎯 **Theme: {vocab_set['theme']}**

"""
    
    for word in vocab_set['words']:
        response += f"• **{word}**\n"
    
    response += f"""
💡 **Challenge:** Use these words in sentences today!

Want organized vocabulary lessons with examples and exercises? 👇
{MAIN_LINK}"""
    
    await update.message.reply_text(response)

async def practice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Iniciar prática de conversação."""
    topics = [
        "Tell me about your favorite hobby! 🎨",
        "What's your dream vacation destination? ✈️",
        "Describe your perfect day! ☀️",
        "What's a skill you'd like to learn? 🎯",
        "Tell me about your hometown! 🏠",
        "What's your favorite type of music? 🎵",
        "Describe your ideal job! 💼",
        "What makes you happy? 😊"
    ]
    
    topic = random.choice(topics)
    
    response = f"""🗣️ **Let's Practice English Together!** 🗣️

Here's your conversation starter:

💬 **{topic}**

Don't worry about making mistakes! I'm here to help you improve! Just share your thoughts, and I'll provide gentle corrections and encouragement! 💪✨

Ready? Go ahead and answer! 🚀"""
    
    await update.message.reply_text(response)

async def responder_com_ia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resposta principal da professora com IA."""
    if not model:
        await fallback_response(update, context)
        return
    
    user_id = update.effective_user.id
    user_texto = update.message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append(f"Student: {user_texto}")
    contexto = "\n".join(user_histories[user_id][-5:])

    try:
        prompt = f"""You are Mrs. Jay's Teaching Assistant, an enthusiastic, patient, and fun English teacher.

        PERSONALITY:
        - You are encouraging, supportive, and never judgmental
        - You make learning fun with emojis and positive energy
        - You gently correct mistakes without making students feel bad
        - You celebrate progress, no matter how small
        - You're knowledgeable but explain things simply
        - You're motivating and help students believe in themselves

        TEACHING STYLE:
        - If students make grammar/vocabulary mistakes, gently correct them
        - Provide encouraging feedback on their English
        - Ask follow-up questions to keep conversation flowing
        - Share relevant tips when appropriate
        - Use encouraging language: "Great job!", "You're improving!", "That's a good question!"
        - Include emojis to make conversations fun

        CONVERSATION APPROACH:
        - Respond naturally to what they say
        - If their English needs improvement, model correct usage
        - Encourage them to keep practicing
        - Occasionally mention resources for further learning
        - Be patient with beginners, challenging with advanced students

        IMPORTANT: 
        - Keep responses conversational, not lecture-like
        - Focus on communication over perfection
        - Make students feel confident about their English journey
        
        Recent conversation:
        {contexto}
        
        Respond as the encouraging English teacher:"""
        
        response = model.generate_content(prompt)
        resposta = response.text
        
        # Adicionar call-to-action ocasionalmente (20% das vezes)
        if random.random() < 0.2:
            resposta += f"\n\n💡 Want more structured English practice? Check out: {MAIN_LINK}"
            
    except Exception as e:
        logger.error(f"Erro na Gemini: {e}")
        await fallback_response(update, context)
        return

    user_histories[user_id].append(f"Teacher: {resposta}")
    await update.message.reply_text(resposta)

async def fallback_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resposta de fallback quando IA não está disponível."""
    responses = [
        "Great question! I love your enthusiasm for learning English! 🌟 Keep practicing!",
        "You're doing wonderful! Every conversation helps you improve! 💪",
        "That's interesting! Can you tell me more about that? 🤔",
        "Excellent! I can see you're really trying - that's what matters most! ✨",
        "Keep going! Practice makes progress, not perfection! 🚀"
    ]
    
    response = random.choice(responses)
    response += f"\n\nFor structured lessons and more practice: {MAIN_LINK}"
    
    await update.message.reply_text(response)

# ---------- SISTEMA DE POSTS EDUCATIVOS ----------

class EnglishTeacherPosts:
    def __init__(self, application, group_id, gemini_api_key):
        self.application = application
        self.group_id = group_id
        self.model = model if gemini_api_key else None
        self.stats = {"posts_enviados": 0, "tips_enviados": 0}
        
    async def create_daily_post(self):
        """Cria post educativo diário."""
        
        if not self.model:
            # Fallback sem IA
            motivational = random.choice(MOTIVATIONAL_PHRASES)
            call_to_action = random.choice(CALL_TO_ACTIONS)
            
            post_text = f"""🎓 **Daily English Inspiration** 🎓

{motivational}

Today's reminder: Every time you use English, you're getting stronger! 💪

{call_to_action}
👉 {MAIN_LINK}

Follow @englishwithmrjay for daily content! 📸
{INSTAGRAM_PROFILE}

#EnglishLearning #Motivation #LearnEnglish"""
            
        else:
            try:
                prompt = """Create an engaging educational post for English learners. Include:
                1. A motivational message about learning English
                2. A practical tip or mini-lesson
                3. Encouragement for daily practice
                
                Keep it positive, educational, and inspiring. Use emojis appropriately.
                Don't include links - they will be added separately.
                """
                
                response = self.model.generate_content(prompt)
                ai_content = response.text
                
                call_to_action = random.choice(CALL_TO_ACTIONS)
                
                post_text = f"""{ai_content}

{call_to_action}
👉 {MAIN_LINK}

🎬 Daily English content: {INSTAGRAM_PROFILE}

#EnglishLearning #Education #LearnWithMrJay"""
                
            except Exception as e:
                logger.error(f"Erro ao gerar post com IA: {e}")
                return await self.create_daily_post()  # Fallback
        
        try:
            await self.application.bot.send_message(
                chat_id=self.group_id,
                text=post_text,
                parse_mode='Markdown'
            )
            self.stats["posts_enviados"] += 1
            logger.info("✅ Post educativo enviado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar post: {e}")

    async def scheduler_loop(self):
        """Loop principal do agendador."""
        logger.info("🕐 Iniciando agendador de posts educativos...")
        
        while True:
            now = datetime.now().time()
            
            # Post às 9:00 da manhã
            if now.hour == 9 and now.minute == 0:
                await self.create_daily_post()
                await asyncio.sleep(60)  # Evitar múltiplos posts
            
            await asyncio.sleep(30)  # Verificar a cada 30 segundos

def setup_english_posts(application, group_id, gemini_api_key):
    """Configura sistema de posts educativos."""
    post_manager = EnglishTeacherPosts(application, group_id, gemini_api_key)
    application.english_post_manager = post_manager
    
    # Iniciar agendador
    asyncio.create_task(post_manager.scheduler_loop())
    
    return post_manager

# ---------- COMANDOS ADMINISTRATIVOS ----------

async def post_now_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Postar agora (admin only)."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Only administrators can use this command.")
        return
    
    if hasattr(context.application, 'english_post_manager'):
        manager = context.application.english_post_manager
        await manager.create_daily_post()
        await update.message.reply_text("✅ Educational post sent!")
    else:
        await update.message.reply_text("❌ Post system not configured.")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Estatísticas do bot."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Only administrators can use this command.")
        return
    
    if hasattr(context.application, 'english_post_manager'):
        manager = context.application.english_post_manager
        stats = manager.stats
        
        stats_text = f"""📊 **English Teacher Bot Stats**

📱 **Posts sent:** {stats['posts_enviados']}
💬 **Active conversations:** {len(user_histories)}
🎯 **Configured group:** {GROUP_ID}

🕐 **Posting schedule:** 9:00 AM daily
🧠 **AI Status:** {'✅ Active' if model else '❌ Disabled'}
"""
    else:
        stats_text = "❌ Statistics not available - post system not configured."
    
    await update.message.reply_text(stats_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status geral do sistema."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Only administrators can use this command.")
        return
    
    status_text = f"""🤖 **English Teacher Bot Status**

🎓 **Conversational Bot:** ✅ Online
📱 **Educational Posts:** {'✅ Active' if GROUP_ID != '@seu_grupo_ingles' else '❌ Not configured'}
🧠 **AI (Gemini):** {'✅ Active' if model else '❌ Disabled'}
📺 **Target Group:** {GROUP_ID}

⏰ **Schedule:** Daily posts at 9:00 AM
💬 **Active chats:** {len(user_histories)}
🔗 **Resources link:** Active

🌟 **Ready to teach English!** 🌟"""
    
    await update.message.reply_text(status_text)

# ---------- FUNÇÃO PRINCIPAL ----------

def main() -> None:
    """Inicializa o English Teacher Bot."""
    
    # Verificar configurações
    if GROUP_ID == "@seu_grupo_ingles":
        logger.warning("⚠️ Configure GROUP_ID to enable automatic posts!")
        print("\n🔧 CONFIGURATION NEEDED:")
        print("1. Edit GROUP_ID with your group/channel ID")
        print("2. Add your ID to ADMIN_IDS")
        print("3. Ensure apikey.txt has your Gemini API key")
    
    # Carregar token
    try:
        with open("token.txt") as tokenfile:
            token = tokenfile.read().strip()
    except FileNotFoundError:
        logger.error("❌ File token.txt not found!")
        return
    
    # Criar aplicação
    application = Application.builder().token(token).build()

    # ---------- CONFIGURAR SISTEMA DE POSTS ----------
    if GEMINI_API_KEY and GROUP_ID != "@seu_grupo_ingles":
        try:
            setup_english_posts(application, GROUP_ID, GEMINI_API_KEY)
            logger.info("✅ Educational posting system configured!")
        except Exception as e:
            logger.error(f"❌ Error configuring posts: {e}")
    else:
        logger.warning("⚠️ Posting system disabled (configure GROUP_ID and API key)")

    # ---------- HANDLERS ----------
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tips", tips_command))
    application.add_handler(CommandHandler("motivation", motivation_command))
    application.add_handler(CommandHandler("resources", resources_command))
    application.add_handler(CommandHandler("grammar", grammar_command))
    application.add_handler(CommandHandler("vocabulary", vocabulary_command))
    application.add_handler(CommandHandler("practice", practice_command))
    
    # Admin commands
    application.add_handler(CommandHandler("post_now", post_now_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("status", status_command))

    # Conversa com IA
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_com_ia))

    # ---------- INICIAR ----------
    logger.info("🎓 Starting English Teacher Bot")
    logger.info(f"👥 Conversations: ✅ Active")
    logger.info(f"📱 Educational Posts: {'✅ Active' if GROUP_ID != '@seu_grupo_ingles' else '❌ Disabled'}")
    logger.info(f"🧠 AI: {'✅ Active' if model else '❌ Disabled'}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()