    #!/usr/bin/env python3
    """
    Teacher Isa Bot - Complete English Learning Assistant
    ===================================================

    Sistema completo de ensino de inglês com:
    1. Conversas educativas e motivadoras  
    2. 1 vídeo diário (do Google Drive)
    3. 3 quizzes em horários diferentes
    4. 1 curiosidade da língua inglesa
    5. Call-to-action para recursos premium

    Bot: @teacher_isa_bot
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

    # Import Google Drive Manager
    from google_drive_manager import GoogleDriveManager, extract_folder_id_from_url

    # Configurar logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler("/Users/jeorgecassiodesousasilva/Documents/PYTHON VS/telegram_bot/english_teacher_bot/teacher_isa.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    # ---------- CONFIGURAÇÃO ----------
    # IMPORTANTE: Configure estes valores!

    GROUP_ID = "@English_teacher"  # Configure com seu grupo/canal
    ADMIN_IDS = [123456789, 8229862045]  # Configure com seu ID

    # Google Drive Configuration
    GOOGLE_DRIVE_FOLDER_URL = "https://drive.google.com/drive/folders/1KslzJkbExVY8X2ZifP6YGiM62BxNRSyc?usp=sharing"
    GOOGLE_DRIVE_FOLDER_ID = "1KslzJkbExVY8X2ZifP6YGiM62BxNRSyc"  # Extraído da URL

    # Links educacionais
    MAIN_LINK = "https://linktr.ee/englishwithmrjay?fbclid=PAZXh0bgNhZW0CMTEAAad4dDVNWKBIsJJuGH-cDmZtFBN3DxwkBQY6Vd5X7QQkVrYC9o_ETW1yOPsuOA_aem_0hqlR-kKzDCKB43TAnezgA"
    INSTAGRAM_PROFILE = "https://www.instagram.com/englishwithmrjay/"

    # Configurações de retry
    MAX_RETRIES = 3
    RETRY_DELAY = 5

    # ---------- CONFIGURAÇÃO GEMINI ----------
    def setup_gemini():
        """Configura Gemini com tratamento de erro."""
        try:
            api_key = None
            
            if os.path.exists("apikey.txt"):
                with open("apikey.txt", "r") as f:
                    api_key = f.read().strip()
            
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
                    await asyncio.sleep(RETRY_DELAY * (2 ** attempt))
                else:
                    logger.error(f"❌ Operação falhou após {MAX_RETRIES} tentativas")
                    raise
            except Exception as e:
                logger.error(f"❌ Erro não recuperável: {e}")
                raise

    # ---------- FRASES E CONTEÚDO ----------
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

    QUIZ_TOPICS = [
        "Grammar basics", "Vocabulary building", "Pronunciation tips",
        "Common phrases", "Business English", "Travel English",
        "Idioms and expressions", "Verb tenses", "Prepositions",
        "Conversation starters"
    ]

    ENGLISH_FACTS = [
        "English has over 170,000 words currently in use! 📚",
        "The word 'set' has the most different meanings in English - over 430! 🤯",
        "English is the official language of the sky - all pilots must speak English! ✈️",
        "Shakespeare invented over 1,700 words that we still use today! 🎭",
        "The longest English word has 45 letters: pneumonoultramicroscopicsilicovolcanoconosis! 😮",
        "English is spoken by over 1.5 billion people worldwide! 🌍",
        "The word 'listen' contains the same letters as 'silent'! 🤫",
        "English is the most commonly used language on the internet! 💻"
    ]

    # ---------- ENVIO SEGURO DE MENSAGENS ----------
    async def safe_send_message(bot, chat_id, text, **kwargs):
        """Envia mensagem com tratamento de erro."""
        try:
            await retry_operation(bot.send_message, chat_id=chat_id, text=text, **kwargs)
            logger.info("✅ Mensagem enviada com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")

    async def safe_send_video(bot, chat_id, video, caption=None, **kwargs):
        """Envia vídeo com tratamento de erro."""
        try:
            # Limitar caption para evitar problemas
            if caption and len(caption) > 1000:
                caption = caption[:997] + "..."
            
            # Limpar caracteres especiais que podem causar problemas de parsing
            if caption:
                caption = caption.replace('**', '').replace('*', '').replace('_', '').replace('`', '')
            
            await retry_operation(bot.send_video, chat_id=chat_id, video=video, caption=caption, **kwargs)
            logger.info("✅ Vídeo enviado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar vídeo: {e}")
            
            # Tentar enviar sem caption se der erro
            try:
                if caption:  # Se tinha caption, tenta sem
                    await retry_operation(bot.send_video, chat_id=chat_id, video=video, **kwargs)
                    logger.info("✅ Vídeo enviado sem caption (fallback)")
            except Exception as e2:
                logger.error(f"❌ Erro no fallback do vídeo: {e2}")

    # ---------- FUNÇÕES DE CONVERSAÇÃO ----------
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Mensagem de boas-vindas da Teacher Isa."""
        user = update.effective_user
        
        welcome_message = f"""Hello {user.first_name}! 👋😊

    I'm Teacher Isa, your personal English learning assistant! 🎓✨

    🌟 **What I offer you:**

    📚 **Interactive Practice** - Chat with me to improve your English!
    🎯 **Daily Content** - Videos, quizzes, and fun facts!
    💡 **Learning Tips** - Practical advice for faster progress
    🎮 **Quiz Challenges** - Test your knowledge throughout the day
    🔍 **English Facts** - Discover amazing things about English!

    **How to practice with me:**
    • Just start chatting - I'll help you improve naturally! 💬
    • Use /quiz for instant English challenges 🧠
    • /fact for interesting English trivia 🤓
    • /tips for learning advice 📝
    • /help to see all my features 🔧

    Remember: Every conversation is practice! Don't worry about mistakes - that's how we learn! 💪

    What would you like to practice today? Let's make English fun! 🚀✨"""
        
        await update.message.reply_text(welcome_message)

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Comandos disponíveis."""
        user_id = update.effective_user.id
        is_admin = user_id in ADMIN_IDS
        
        base_commands = """📚 **Available Commands:**

    🎯 **Interactive Learning:**
    /quiz - Take an instant English quiz with polls! 🧠
    /fact - Learn a fun English fact! 🤓  
    /tips - Get practical learning tips 📝
    /motivation - Daily motivation boost ⭐
    /practice - Start conversation practice 💬
    /resources - Access premium materials 🎯

    ✨ **Just talk to me!** 
    I'll help you practice English naturally while we chat! 🗣️

    🎮 **New Feature:** Interactive quiz polls with instant feedback!

    Remember: The best way to learn is by using English! 💪"""

        admin_commands = """

    🔧 **Admin Commands:**
    /post_video - Post daily video now 🎬
    /post_quiz - Post quiz now 🧠
    /post_fact - Post English fact now 🤓
    /stats - View bot statistics 📊
    /health - Check system status 🏥

    🌐 **Google Drive Commands:**
    /drive_sync - Sync videos from Google Drive 🔄
    /drive_test - Test video download 🎬
    /drive_cache - Manage video cache 🗂️"""

        answer = base_commands + (admin_commands if is_admin else "")
        await update.message.reply_text(answer)

    async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Quiz instantâneo usando Poll do Telegram."""
        try:
            if model:
                topic = random.choice(QUIZ_TOPICS)
                prompt = f"""Create a fun English quiz question about {topic}.

    Return ONLY in this exact JSON format:
    {{
        "question": "Your question here?",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
        "correct_answer": 0,
        "explanation": "Brief explanation (max 100 characters)"
    }}

    The correct_answer should be the index (0-3) of the correct option.
    Keep it educational but fun. Make the question clear and concise.
    IMPORTANT: Keep explanation under 100 characters!"""

                try:
                    response = await asyncio.wait_for(
                        asyncio.to_thread(model.generate_content, prompt),
                        timeout=10.0
                    )
                    
                    # Tentar extrair JSON da resposta
                    import json
                    response_text = response.text.strip()
                    
                    # Encontrar o JSON na resposta
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != -1:
                        json_str = response_text[start_idx:end_idx]
                        quiz_data = json.loads(json_str)
                    else:
                        raise ValueError("JSON não encontrado na resposta")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar resposta da IA: {e} - usando fallback")
                    quiz_data = get_fallback_quiz_data()
            else:
                quiz_data = get_fallback_quiz_data()

            # Criar poll do Telegram
            # Limitar explicação para evitar erro de mensagem muito longa
            explanation = quiz_data['explanation'][:150] + "..." if len(quiz_data['explanation']) > 150 else quiz_data['explanation']
            
            await update.message.reply_poll(
                question=f"🧠 {quiz_data['question']}",
                options=quiz_data['options'],
                type='quiz',
                correct_option_id=quiz_data['correct_answer'],
                explanation=f"✅ {explanation}",
                is_anonymous=False,
                allows_multiple_answers=False
            )
            
            logger.info("✅ Quiz poll enviado com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro em quiz_command: {e}")
            # Fallback para quiz texto se poll falhar
            await update.message.reply_text("Let me create a quiz for you! 🧠\n\nWhat's the past tense of 'go'?\nA) Goed\nB) Went\nC) Gone\nD) Going\n\nReply with your answer! 📝")

    def get_fallback_quiz():
        """Quiz de fallback quando IA falha."""
        quizzes = [
            """**Quiz Time! 🧠**

    What's the correct past tense of "go"?

    A) Goed
    B) Went  
    C) Gone
    D) Going

    Answer in the comments! 📝""",

            """**Quiz Time! 🧠**

    Which sentence is correct?

    A) I am going to the store
    B) I going to the store
    C) I goes to the store  
    D) I went to the store yesterday

    Think carefully! 🤔""",

            """**Quiz Time! 🧠**

    What does "break a leg" mean?

    A) Hurt yourself
    B) Good luck
    C) Run fast
    D) Sit down

    It's an idiom! 😊"""
        ]
        
        return random.choice(quizzes)

    def get_fallback_quiz_data():
        """Dados estruturados para quiz poll quando IA falha."""
        quiz_options = [
            {
                "question": "What's the correct past tense of 'go'?",
                "options": ["Goed", "Went", "Gone", "Going"],
                "correct_answer": 1,
                "explanation": "Past tense of 'go' is 'went'. 'Gone' is past participle!"
            },
            {
                "question": "Which sentence is grammatically correct?",
                "options": [
                    "I am going to the store",
                    "I going to the store", 
                    "I goes to the store",
                    "I are going to the store"
                ],
                "correct_answer": 0,
                "explanation": "Use 'am' with 'I'. Subject-verb agreement is key!"
            },
            {
                "question": "What does the idiom 'break a leg' mean?",
                "options": ["Hurt yourself", "Good luck", "Run fast", "Sit down"],
                "correct_answer": 1,
                "explanation": "In theater, 'break a leg' means 'good luck'!"
            },
            {
                "question": "Which word is a synonym for 'happy'?",
                "options": ["Sad", "Joyful", "Angry", "Tired"],
                "correct_answer": 1,
                "explanation": "Joyful means very happy! Great for vocabulary building."
            },
            {
                "question": "What's the plural of 'child'?",
                "options": ["Childs", "Children", "Childes", "Child"],
                "correct_answer": 1,
                "explanation": "Children is the irregular plural. English has many!"
            }
        ]
        
        return random.choice(quiz_options)

    async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Lida com respostas aos polls de quiz."""
        try:
            poll_answer = update.poll_answer
            user = poll_answer.user
            selected_options = poll_answer.option_ids
            
            if selected_options:
                # Mensagem motivacional para quem participou
                motivational_responses = [
                    f"Great job participating, {user.first_name}! 🌟",
                    f"Thanks for taking the quiz, {user.first_name}! 💪", 
                    f"Keep learning, {user.first_name}! 📚",
                    f"Awesome participation, {user.first_name}! 🎯"
                ]
                
                response = random.choice(motivational_responses)
                
                # Enviar mensagem privada motivacional (se possível)
                try:
                    await context.bot.send_message(
                        chat_id=user.id,
                        text=f"{response}\n\nEvery quiz makes you stronger! 💪\n\nKeep practicing: {MAIN_LINK}"
                    )
                except Exception:
                    # Se não conseguir enviar privada, log apenas
                    logger.info(f"✅ Quiz respondido por {user.first_name} (ID: {user.id})")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao processar resposta do poll: {e}")

    async def tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Dicas de aprendizado."""
        tips = [
            "🎯 **Daily Practice Tip:**\nSpeak English for just 5 minutes daily - even to yourself!",
            "📚 **Vocabulary Tip:**\nLearn 3 new words daily and use them in sentences!",
            "🎵 **Listening Tip:**\nWatch English videos with subtitles, then without!",
            "✍️ **Writing Tip:**\nKeep an English diary - write about your day!",
            "🗣️ **Speaking Tip:**\nRecord yourself speaking and listen back!",
            "📖 **Reading Tip:**\nRead English news for 10 minutes daily!",
            "🧠 **Memory Tip:**\nCreate mental pictures for new vocabulary!",
            "⏰ **Time Management:**\nStudy English in small chunks throughout the day!"
        ]
        
        selected_tip = random.choice(tips)
        
        tip_message = f"""{selected_tip}

    💡 **Remember:** Consistency beats perfection!

    Want personalized learning plans? 👇
    {MAIN_LINK}"""
        
        await update.message.reply_text(tip_message)

    async def motivation_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Motivação diária."""
        motivation = random.choice(MOTIVATIONAL_PHRASES)
        
        motivation_message = f"""⭐ **Daily Motivation**

    {motivation}

    Remember: You're not just learning English - you're opening doors to the world! 🌍

    Each word you learn, each sentence you speak, brings you closer to fluency! 

    🔥 **Today's challenge:** Use one new English word in conversation!

    Ready to accelerate your progress? 👇
    {MAIN_LINK}"""
        
        await update.message.reply_text(motivation_message)

    async def resources_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Recursos premium."""
        resources_message = f"""🎯 **Premium English Resources**

    🌟 **What you'll get:**
    ✅ Structured lesson plans
    ✅ Personalized coaching  
    ✅ Interactive exercises
    ✅ Progress tracking
    ✅ Speaking practice sessions
    ✅ Business English modules

    🚀 **Transform your English today:**
    {MAIN_LINK}

    📸 **Daily content & tips:**
    {INSTAGRAM_PROFILE}

    🎓 **Why choose our method:**
    • Practical, real-world English
    • Fun and engaging approach  
    • Proven results
    • Supportive community

    Ready to level up? Click the link above! ⬆️"""
        
        await update.message.reply_text(resources_message)

    async def practice_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Iniciar prática de conversação."""
        practice_starters = [
            "Let's practice! Tell me about your day in English! 😊",
            "Ready to practice? Describe your favorite food in English! 🍕",
            "Practice time! What's your dream vacation destination? 🏖️",
            "Let's chat! Tell me about your hobbies in English! 🎨",
            "Practice session! Describe the weather today! ☀️",
            "Conversation practice! What's your favorite movie and why? 🎬"
        ]
        
        starter = random.choice(practice_starters)
        
        practice_message = f"""💬 **Conversation Practice**

    {starter}

    💡 **Tips for practice:**
    • Don't worry about mistakes
    • Speak your thoughts freely  
    • I'll help you improve naturally
    • Every sentence is progress!

    Remember: The goal is communication, not perfection! 🎯"""
        
        await update.message.reply_text(practice_message)

    async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Curiosidade sobre inglês."""
        fact = random.choice(ENGLISH_FACTS)
        
        fact_message = f"""🤓 **Fun English Fact!**

    {fact}

    Isn't English amazing? The more you learn, the more fascinating it becomes! 

    Ready to dive deeper into English? 👇
    {MAIN_LINK}

    Follow us for daily English content! 📸
    {INSTAGRAM_PROFILE}"""
        
        await update.message.reply_text(fact_message)

    async def responder_com_ia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Resposta principal com IA."""
        try:
            user_id = update.effective_user.id
            user_texto = update.message.text

            if user_id not in user_histories:
                user_histories[user_id] = []

            user_histories[user_id].append(f"Student: {user_texto}")
            
            if len(user_histories[user_id]) > 10:
                user_histories[user_id] = user_histories[user_id][-10:]

            contexto = "\n".join(user_histories[user_id][-5:])

            if model:
                try:
                    prompt = f"""You are Teacher Isa, an enthusiastic and patient English teacher. 

    PERSONALITY:
    - Encouraging and supportive, never judgmental
    - Make learning fun with emojis and positive energy  
    - Gently correct mistakes without making students feel bad
    - Celebrate all progress, no matter how small
    - Explain things simply and clearly
    - Motivating and help students believe in themselves

    TEACHING STYLE:
    - If they make mistakes, gently model the correct way
    - Give encouraging feedback on their English
    - Ask follow-up questions to practice more
    - Share relevant tips when helpful
    - Use phrases like "Great job!", "You're improving!", "Good question!"
    - Keep it conversational, not lecture-like

    Recent conversation:
    {contexto}

    Respond as Teacher Isa (keep under 150 words):"""
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(model.generate_content, prompt),
                        timeout=10.0
                    )
                    
                    resposta = response.text
                    
                    # Adicionar call-to-action ocasionalmente
                    if random.random() < 0.15:
                        resposta += f"\n\n🔗 More English resources: {MAIN_LINK}"
                    
                    user_histories[user_id].append(f"Teacher Isa: {resposta}")
                    await update.message.reply_text(resposta)
                    return
                    
                except Exception as e:
                    logger.warning(f"⚠️ Erro na IA: {e} - usando fallback")

            # Fallback inteligente
            resposta = generate_smart_fallback(user_texto)
            user_histories[user_id].append(f"Teacher Isa: {resposta}")
            await update.message.reply_text(resposta)
            
        except Exception as e:
            logger.error(f"❌ Erro em responder_com_ia(): {e}")
            await update.message.reply_text("I'm here to help you practice English! What would you like to talk about? 😊")

    def generate_smart_fallback(user_text):
        """Gera resposta inteligente sem IA."""
        text_lower = user_text.lower()
        
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'good morning']):
            return "Hello! Great to see you practicing English! What would you like to talk about today? 😊"
        elif any(word in text_lower for word in ['help', 'how', 'what', 'why']):
            return "Great question! That shows you're thinking in English! 🧠 Keep asking questions - that's how we learn!"
        elif any(word in text_lower for word in ['thank', 'thanks', 'good', 'great']):
            return f"You're very welcome! {random.choice(MOTIVATIONAL_PHRASES)} Keep practicing! 💪"
        else:
            return f"I love that you're practicing! {random.choice(MOTIVATIONAL_PHRASES)} Tell me more! 😊"

    # ---------- SISTEMA DE POSTS AUTOMÁTICOS ----------
    class TeacherIsaPostingSystem:
        def __init__(self, application, group_id):
            self.application = application
            self.group_id = group_id
            self.model = model
            self.stats = {
                "videos_enviados": 0,
                "quizzes_enviados": 0, 
                "facts_enviados": 0,
                "falhas": 0
            }
            
            # Initialize Google Drive Manager
            self.drive_manager = GoogleDriveManager(GOOGLE_DRIVE_FOLDER_ID)
            self.drive_initialized = False
            
        async def initialize_drive(self):
            """Inicializa conexão com Google Drive."""
            try:
                self.drive_initialized = await self.drive_manager.initialize()
                if self.drive_initialized:
                    logger.info("✅ Google Drive conectado - vídeos serão baixados automaticamente!")
                else:
                    logger.warning("⚠️ Google Drive não disponível - usando modo fallback")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar Google Drive: {e}")
                self.drive_initialized = False
            
        async def post_daily_video(self):
            """Posta vídeo diário com comentário educativo."""
            try:
                video_path = None
                
                # Tentar obter vídeo do Google Drive primeiro
                if self.drive_initialized:
                    try:
                        logger.info("🌐 Obtendo vídeo do Google Drive...")
                        video_path = await self.drive_manager.get_random_video()
                        if video_path:
                            logger.info(f"✅ Vídeo obtido do Google Drive: {video_path}")
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao obter vídeo do Google Drive: {e}")
                
                # Fallback para pasta local se Google Drive falhar
                if not video_path:
                    logger.info("📁 Verificando pasta local de vídeos...")
                    video_folder = Path("reels_content")
                    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
                    videos = []
                    
                    if video_folder.exists():
                        for ext in video_extensions:
                            videos.extend(video_folder.glob(f"*{ext}"))
                    
                    if videos:
                        # Selecionar vídeo aleatório local
                        selected_video = random.choice(videos)
                        video_path = str(selected_video)
                        logger.info(f"✅ Vídeo local selecionado: {selected_video.name}")
                
                # Postar vídeo se encontrado
                if video_path and os.path.exists(video_path):
                    # Criar comentário educativo
                    comment = await self.create_video_comment()
                    
                    # Enviar vídeo
                    with open(video_path, 'rb') as video_file:
                        await safe_send_video(
                            self.application.bot,
                            self.group_id,
                            video_file,
                            caption=comment,
                            parse_mode=None  # Remover Markdown para evitar erro de parsing
                        )
                    
                    self.stats["videos_enviados"] += 1
                    video_name = os.path.basename(video_path)
                    logger.info(f"✅ Vídeo postado: {video_name}")
                    
                    # Limpar cache do Google Drive periodicamente
                    if self.drive_initialized and random.random() < 0.1:  # 10% chance
                        await self.drive_manager.cleanup_cache()
                        
                else:
                    # Post apenas texto se não há vídeos
                    logger.warning("⚠️ Nenhum vídeo disponível - postando conteúdo texto")
                    await self.post_text_content()
                    
            except Exception as e:
                self.stats["falhas"] += 1
                logger.error(f"❌ Erro ao postar vídeo: {e}")
                logger.error(traceback.format_exc())
        
        async def create_video_comment(self):
            """Cria comentário educativo para vídeo."""
            if self.model:
                try:
                    prompt = """Create an engaging comment for an English learning video from @englishwithmrjay.

    The comment should:
    1. Praise the teaching method
    2. Highlight a key learning point  
    3. Motivate viewers to practice
    4. Be enthusiastic and supportive

    Keep it professional, educational, and encouraging. Use emojis appropriately.
    Don't include links - they will be added separately.
    IMPORTANT: Use only plain text, no special formatting."""
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(self.model.generate_content, prompt),
                        timeout=10.0
                    )
                    content = response.text
                except:
                    content = self.get_fallback_video_comment()
            else:
                content = self.get_fallback_video_comment()
            
            # Limpar formatação especial para evitar erros de parsing
            content = content.replace('**', '').replace('*', '').replace('_', '').replace('`', '')
            
            full_comment = f"""{content}

    🔗 Premium English lessons: {MAIN_LINK}
    📸 Daily content: {INSTAGRAM_PROFILE}

    #EnglishLearning #LearnWithMrJay #Education"""
            
            return full_comment
        
        def get_fallback_video_comment(self):
            """Comentário de fallback para vídeos."""
            comments = [
                """🎬 Amazing English lesson from @englishwithmrjay! 

    This is exactly what makes learning effective! 📚✨

    Key takeaway: Practice daily, even if it's just 5 minutes! 

    Ready to level up your English? 👇""",

                """🌟 Love this teaching approach! 

    Mr. Jay makes English so accessible and fun! 💪

    Remember: Consistency beats perfection in language learning!

    Want more structured lessons? 👇""",

                """📚 Perfect example of practical English! 

    This is why we learn with @englishwithmrjay - real English for real life! 🎯

    Pro tip: Watch, practice, repeat!

    Ready for personalized coaching? 👇"""
            ]
            
            selected = random.choice(comments)
            # Limpar formatação especial
            return selected.replace('**', '').replace('*', '').replace('_', '').replace('`', '')
        
        async def post_quiz(self):
            """Posta quiz educativo usando Poll do Telegram."""
            try:
                if self.model:
                    topic = random.choice(QUIZ_TOPICS)
                    prompt = f"""Create an engaging English quiz about {topic}.

    Return ONLY in this exact JSON format:
    {{
        "question": "Your question here?",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
        "correct_answer": 0,
        "explanation": "Brief explanation (max 100 characters)"
    }}

    The correct_answer should be the index (0-3) of the correct option.
    Make it educational but fun. Question should be clear and concise.
    IMPORTANT: Keep explanation under 100 characters!"""

                    try:
                        response = await asyncio.wait_for(
                            asyncio.to_thread(self.model.generate_content, prompt),
                            timeout=10.0
                        )
                        
                        # Tentar extrair JSON da resposta
                        import json
                        response_text = response.text.strip()
                        
                        # Encontrar o JSON na resposta
                        start_idx = response_text.find('{')
                        end_idx = response_text.rfind('}') + 1
                        
                        if start_idx != -1 and end_idx != -1:
                            json_str = response_text[start_idx:end_idx]
                            quiz_data = json.loads(json_str)
                        else:
                            raise ValueError("JSON não encontrado na resposta")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao processar quiz da IA: {e} - usando fallback")
                        quiz_data = get_fallback_quiz_data()
                else:
                    quiz_data = get_fallback_quiz_data()

                # Criar poll interativo
                # Limitar explicação para evitar erro de mensagem muito longa
                explanation = quiz_data['explanation'][:120] + "..." if len(quiz_data['explanation']) > 120 else quiz_data['explanation']
                
                await self.application.bot.send_poll(
                    chat_id=self.group_id,
                    question=f"🧠 Quiz Challenge: {quiz_data['question']}",
                    options=quiz_data['options'],
                    type='quiz',
                    correct_option_id=quiz_data['correct_answer'],
                    explanation=f"✅ {explanation}",
                    is_anonymous=False,
                    allows_multiple_answers=False
                )
                
                self.stats["quizzes_enviados"] += 1
                logger.info("✅ Quiz poll postado com sucesso!")
                
            except Exception as e:
                self.stats["falhas"] += 1
                logger.error(f"❌ Erro ao postar quiz: {e}")
                
                # Fallback para texto se poll falhar
                try:
                    fallback_quiz = get_fallback_quiz()
                    await safe_send_message(
                        self.application.bot,
                        self.group_id,
                        fallback_quiz + f"\n\n🎯 More quizzes: {MAIN_LINK}",
                        parse_mode='Markdown'
                    )
                    logger.info("✅ Quiz fallback (texto) enviado!")
                except Exception as fallback_error:
                    logger.error(f"❌ Erro no fallback do quiz: {fallback_error}")
        
        async def post_english_fact(self):
            """Posta curiosidade sobre inglês."""
            try:
                fact = random.choice(ENGLISH_FACTS)
                
                fact_post = f"""🤓 **Did You Know?**

    {fact}

    English is full of surprises! The more you explore, the more fascinating it becomes! 

    Each fun fact is a step towards fluency! 🚀

    🌟 **Ready to discover more?**
    Get structured lessons and amazing content:
    {MAIN_LINK}

    Follow for daily English tips: {INSTAGRAM_PROFILE}

    #EnglishFacts #DidYouKnow #LearnEnglish #Education"""

                await safe_send_message(
                    self.application.bot,
                    self.group_id,
                    fact_post,
                    parse_mode='Markdown'
                )
                
                self.stats["facts_enviados"] += 1
                logger.info("✅ Curiosidade postada com sucesso!")
                
            except Exception as e:
                self.stats["falhas"] += 1
                logger.error(f"❌ Erro ao postar curiosidade: {e}")
        
        async def post_text_content(self):
            """Post de conteúdo apenas texto (fallback)."""
            try:
                motivational = random.choice(MOTIVATIONAL_PHRASES)
                
                text_post = f"""🎓 **Daily English Inspiration**

    {motivational}

    Today's reminder: Every conversation in English makes you stronger! 💪

    Small daily practice = Big results! 📈

    🔗 Transform your English today: {MAIN_LINK}
    📸 Follow us: {INSTAGRAM_PROFILE}

    #EnglishLearning #Motivation #Education"""

                await safe_send_message(
                    self.application.bot,
                    self.group_id,
                    text_post,
                    parse_mode='Markdown'
                )
                
                logger.info("✅ Post texto enviado com sucesso!")
                
            except Exception as e:
                logger.error(f"❌ Erro ao postar texto: {e}")
        
        async def scheduler_loop(self):
            """Loop do agendador com horários específicos."""
            logger.info("🕐 Iniciando agendador Teacher Isa...")
            
            while True:
                try:
                    now = datetime.now()
                    hour = now.hour
                    minute = now.minute
                    
                    # 09:00 - Vídeo diário
                    if hour == 9 and minute == 0:
                        await self.post_daily_video()
                        await asyncio.sleep(60)
                    
                    # 12:00 - Quiz 1
                    elif hour == 12 and minute == 0:
                        await self.post_quiz()
                        await asyncio.sleep(60)
                    
                    # 15:00 - Quiz 2  
                    elif hour == 15 and minute == 0:
                        await self.post_quiz()
                        await asyncio.sleep(60)
                    
                    # 18:00 - Quiz 3
                    elif hour == 18 and minute == 0:
                        await self.post_quiz()
                        await asyncio.sleep(60)
                    
                    # 21:00 - Curiosidade
                    elif hour == 21 and minute == 0:
                        await self.post_english_fact()
                        await asyncio.sleep(60)
                    
                    await asyncio.sleep(30)  # Verificar a cada 30 segundos
                    
                except Exception as e:
                    logger.error(f"❌ Erro no scheduler: {e}")
                    await asyncio.sleep(60)

    def setup_posting_system(application, group_id):
        """Configura sistema de postagens."""
        posting_system = TeacherIsaPostingSystem(application, group_id)
        
        # Usar uma forma diferente de anexar ao application
        if not hasattr(application, '_user_data'):
            application._user_data = {}
        application._user_data['posting_system'] = posting_system
        
        return posting_system

    async def start_posting_system(application):
        """Inicia o sistema de postagens após o bot estar rodando."""
        try:
            if hasattr(application, '_user_data') and 'posting_system' in application._user_data:
                posting_system = application._user_data['posting_system']
                
                # Inicializar Google Drive
                logger.info("🌐 Inicializando Google Drive...")
                await posting_system.initialize_drive()
                
                # Criar a tarefa do agendador
                asyncio.create_task(posting_system.scheduler_loop())
                logger.info("✅ Sistema de postagens automáticas iniciado!")
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar postagens: {e}")

    # ---------- COMANDOS ADMINISTRATIVOS ----------
    async def post_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Postar vídeo agora (admin)."""
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Only administrators can use this command.")
            return
        
        if hasattr(context.application, '_user_data') and 'posting_system' in context.application._user_data:
            manager = context.application._user_data['posting_system']
            await manager.post_daily_video()
            await update.message.reply_text("✅ Daily video posted!")
        else:
            await update.message.reply_text("❌ Posting system not configured.")

    async def post_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Postar quiz agora (admin)."""
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Only administrators can use this command.")
            return
        
        if hasattr(context.application, '_user_data') and 'posting_system' in context.application._user_data:
            manager = context.application._user_data['posting_system']
            await manager.post_quiz()
            await update.message.reply_text("✅ Quiz posted!")
        else:
            await update.message.reply_text("❌ Posting system not configured.")

    async def post_fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Postar curiosidade agora (admin)."""
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Only administrators can use this command.")
            return
        
        if hasattr(context.application, '_user_data') and 'posting_system' in context.application._user_data:
            manager = context.application._user_data['posting_system']
            await manager.post_english_fact()
            await update.message.reply_text("✅ English fact posted!")
        else:
            await update.message.reply_text("❌ Posting system not configured.")

    async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Estatísticas do bot."""
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Only administrators can use this command.")
            return
        
        if hasattr(context.application, '_user_data') and 'posting_system' in context.application._user_data:
            manager = context.application._user_data['posting_system']
            stats = manager.stats
            
            # Obter estatísticas do Google Drive
            drive_status = "✅ Connected" if manager.drive_initialized else "❌ Disconnected"
            cache_stats = await manager.drive_manager.get_cache_stats() if manager.drive_initialized else {"files": 0, "size_mb": 0}
            
            stats_text = f"""📊 **Teacher Isa Bot Statistics**

    📹 **Videos posted:** {stats['videos_enviados']}
    🧠 **Quizzes posted:** {stats['quizzes_enviados']}  
    🤓 **Facts posted:** {stats['facts_enviados']}
    ❌ **Failures:** {stats['falhas']}
    💬 **Active conversations:** {len(user_histories)}

    � **Google Drive:** {drive_status}
    📁 **Video cache:** {cache_stats['files']} files ({cache_stats['size_mb']} MB)

    �🎯 **Target group:** {GROUP_ID}
    🕐 **Schedule:**
    - 09:00: Daily video (from Google Drive)
    - 12:00, 15:00, 18:00: Quizzes  
    - 21:00: English fact

    🧠 **AI Status:** {'✅ Active' if model else '❌ Disabled'}"""
        else:
            stats_text = "❌ Statistics not available - posting system not configured."
        
        await update.message.reply_text(stats_text)

    async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status de saúde do sistema."""
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Admin only command.")
            return
        
        try:
            bot_status = "✅ Online"
            ai_status = "✅ Active" if model else "❌ Disabled"
            
            if hasattr(context.application, '_user_data') and 'posting_system' in context.application._user_data:
                posting_status = "✅ Active"
                stats = context.application._user_data['posting_system'].stats
            else:
                posting_status = "❌ Not configured"
                stats = {"videos_enviados": 0, "quizzes_enviados": 0, "facts_enviados": 0}
            
            health_report = f"""🏥 **Teacher Isa System Health**

    🤖 **Bot:** {bot_status}
    🧠 **AI:** {ai_status}  
    📱 **Auto-posting:** {posting_status}
    💬 **Active chats:** {len(user_histories)}

    📊 **Content posted today:**
    🎬 Videos: {stats['videos_enviados']}
    🧠 Quizzes: {stats['quizzes_enviados']}
    🤓 Facts: {stats['facts_enviados']}

    ⏰ **Next posts:**
    - 09:00: Daily video
    - 12:00, 15:00, 18:00: Quizzes
    - 21:00: English fact

    All systems ready to teach! 🎓✨"""
            
            await update.message.reply_text(health_report)
            
        except Exception as e:
            logger.error(f"Erro em health_command: {e}")
            await update.message.reply_text("❌ Error generating health report")

    async def drive_sync_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sincronizar vídeos do Google Drive (admin)."""
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Only administrators can use this command.")
            return
        
        try:
            if hasattr(context.application, '_user_data') and 'posting_system' in context.application._user_data:
                manager = context.application._user_data['posting_system']
                
                if not manager.drive_initialized:
                    await update.message.reply_text("❌ Google Drive not connected.")
                    return
                
                await update.message.reply_text("🔄 Synchronizing videos from Google Drive...")
                
                videos = await manager.drive_manager.sync_videos(force=True)
                cache_stats = await manager.drive_manager.get_cache_stats()
                
                sync_report = f"""✅ **Google Drive Sync Complete**

    📹 **Videos found:** {len(videos)}
    📁 **Cached locally:** {sum(1 for v in videos if v.get('cached', False))}
    💾 **Cache size:** {cache_stats['size_mb']} MB

    🎬 **Recent videos:**"""

                # Mostrar até 5 vídeos mais recentes
                for i, video in enumerate(videos[:5]):
                    status = "📁" if video.get('cached') else "🌐"
                    sync_report += f"\n{status} {video['name'][:40]}..."
                    
                await update.message.reply_text(sync_report)
            else:
                await update.message.reply_text("❌ Posting system not configured.")
                
        except Exception as e:
            logger.error(f"❌ Erro em drive_sync_command: {e}")
            await update.message.reply_text(f"❌ Error syncing: {str(e)}")

    async def drive_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Testar download de vídeo do Google Drive (admin)."""
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Only administrators can use this command.")
            return
        
        try:
            if hasattr(context.application, '_user_data') and 'posting_system' in context.application._user_data:
                manager = context.application._user_data['posting_system']
                
                if not manager.drive_initialized:
                    await update.message.reply_text("❌ Google Drive not connected.")
                    return
                
                await update.message.reply_text("🎬 Testing Google Drive video download...")
                
                video_path = await manager.drive_manager.get_random_video()
                
                if video_path:
                    video_name = os.path.basename(video_path)
                    file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
                    
                    test_report = f"""✅ **Test Successful!**

    📹 **Video:** {video_name}
    💾 **Size:** {file_size:.1f} MB
    📁 **Local path:** {video_path}

    Ready to post videos from Google Drive! 🎯"""
                    
                    await update.message.reply_text(test_report)
                else:
                    await update.message.reply_text("❌ No videos found or download failed.")
            else:
                await update.message.reply_text("❌ Posting system not configured.")
                
        except Exception as e:
            logger.error(f"❌ Erro em drive_test_command: {e}")
            await update.message.reply_text(f"❌ Test failed: {str(e)}")

    async def drive_cache_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gerenciar cache do Google Drive (admin)."""
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("❌ Only administrators can use this command.")
            return
        
        try:
            if hasattr(context.application, '_user_data') and 'posting_system' in context.application._user_data:
                manager = context.application._user_data['posting_system']
                
                if not manager.drive_initialized:
                    await update.message.reply_text("❌ Google Drive not connected.")
                    return
                
                # Limpar cache
                await manager.drive_manager.cleanup_cache(max_size_mb=200)  # Limitar a 200MB
                
                # Obter estatísticas atualizadas
                cache_stats = await manager.drive_manager.get_cache_stats()
                
                cache_report = f"""🧹 **Cache Cleanup Complete**

    📁 **Files in cache:** {cache_stats['files']}
    💾 **Total size:** {cache_stats['size_mb']} MB
    📊 **Cache limit:** 200 MB

    Cache optimized for performance! ⚡"""
                
                await update.message.reply_text(cache_report)
            else:
                await update.message.reply_text("❌ Posting system not configured.")
                
        except Exception as e:
            logger.error(f"❌ Erro em drive_cache_command: {e}")
            await update.message.reply_text(f"❌ Cache management failed: {str(e)}")

    # ---------- FUNÇÃO PRINCIPAL ----------
    def main() -> None:
        """Função principal do Teacher Isa Bot."""
        logger.info("🎓 Iniciando Teacher Isa Bot (@teacher_isa_bot)")
        
        try:
            # Verificar configurações
            logger.info(f"✅ GROUP_ID configurado: {GROUP_ID}")
            logger.info(f"✅ ADMIN_IDS configurados: {ADMIN_IDS}")
            print("\n🎓 Teacher Isa Bot - Configuração:")
            print(f"📺 Canal/Grupo: {GROUP_ID}")
            print(f"👨‍💼 Admins: {len(ADMIN_IDS)} configurados")
            print("📁 Adicione vídeos na pasta reels_content/ para postagens automáticas")
            
            # Carregar token
            try:
                with open("token.txt") as tokenfile:
                    token = tokenfile.read().strip()
                    logger.info("✅ Token carregado com sucesso!")
            except FileNotFoundError:
                logger.error("❌ Arquivo token.txt não encontrado!")
                return
            
            # Criar aplicação
            application = Application.builder()\
                .token(token)\
                .connect_timeout(30.0)\
                .read_timeout(30.0)\
                .write_timeout(30.0)\
                .build()

            # Configurar sistema de posts
            try:
                setup_posting_system(application, GROUP_ID)
                logger.info("✅ Sistema de postagens automáticas configurado!")
                logger.info("🕐 Horários: 9h(vídeo) | 12h,15h,18h(quiz) | 21h(curiosidade)")
                
                # Adicionar callback para iniciar posts após bot estar online
                async def post_init(app):
                    await start_posting_system(app)
                
                application.post_init = post_init
                
            except Exception as e:
                logger.error(f"❌ Erro ao configurar postagens: {e}")

            # Handlers
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("help", help_command))
            application.add_handler(CommandHandler("quiz", quiz_command))
            application.add_handler(CommandHandler("fact", fact_command))
            application.add_handler(CommandHandler("tips", tips_command))
            application.add_handler(CommandHandler("motivation", motivation_command))
            application.add_handler(CommandHandler("resources", resources_command))
            application.add_handler(CommandHandler("practice", practice_command))
            
            # Poll handlers
            from telegram.ext import PollAnswerHandler
            application.add_handler(PollAnswerHandler(handle_poll_answer))
            
            # Admin commands
            application.add_handler(CommandHandler("post_video", post_video_command))
            application.add_handler(CommandHandler("post_quiz", post_quiz_command))
            application.add_handler(CommandHandler("post_fact", post_fact_command))
            application.add_handler(CommandHandler("stats", stats_command))
            application.add_handler(CommandHandler("health", health_command))
            
            # Google Drive admin commands
            application.add_handler(CommandHandler("drive_sync", drive_sync_command))
            application.add_handler(CommandHandler("drive_test", drive_test_command))
            application.add_handler(CommandHandler("drive_cache", drive_cache_command))

            # Conversa com IA
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_com_ia))

            # Iniciar
            logger.info("🚀 Teacher Isa Bot iniciado!")
            logger.info(f"👥 Conversação: ✅ Ativa")
            logger.info(f"📱 Posts automáticos: ✅ Ativos para {GROUP_ID}")
            logger.info(f"🧠 IA: {'✅ Ativa' if model else '❌ Desabilitada'}")
            logger.info("🕐 Horários: 9h(vídeo) | 12h,15h,18h(quiz) | 21h(curiosidade)")
            
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except KeyboardInterrupt:
            logger.info("🛑 Teacher Isa Bot encerrado pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro crítico: {e}")
            logger.error(traceback.format_exc())

    if __name__ == "__main__":
        main()