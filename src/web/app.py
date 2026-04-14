"""
Streamlit UI for Teacher Isa AI.
Interactive English learning assistant with RAG-powered responses.
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
from dotenv import load_dotenv

# --- Garantir que a raiz do projeto esteja no sys.path (apenas para desenvolvimento) ---
ROOT = Path(__file__).resolve().parents[1]  # project_root/src/web -> parents[1] = project_root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Carrega as variáveis de ambiente (como GROQ_API_KEY do .env)
load_dotenv()

# Agora podemos importar módulos do pacote src
from src.engine import get_chat_engine
from src.model_loader import get_llm_singleton, get_embedding_singleton
# Se usar RAGSystem, importe e inicialize; caso contrário, remova
from src.core.rag import RAGSystem  # ajuste se o caminho for diferente

import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Teacher Isa",
    page_icon="📚",
    layout="wide"
)

# Inicializa RAG/Chat engine apenas uma vez usando cache do Streamlit
@st.cache_resource
def init_chat_engine():
    try:
        llm = get_llm_singleton()
        embed = get_embedding_singleton()
        chat_engine = get_chat_engine(llm, embed)
        # Se você tem um RAGSystem que gerencia documentos, inicialize aqui
        try:
            rag_system = RAGSystem(chat_engine)  # ajuste construtor conforme sua implementação
        except Exception:
            rag_system = None
        return {"chat_engine": chat_engine, "rag_system": rag_system}
    except Exception as e:
        logger.exception("Erro ao inicializar Chat Engine: %s", e)
        return {"chat_engine": None, "rag_system": None}

resources = init_chat_engine()
chat_engine = resources.get("chat_engine")
rag_system = resources.get("rag_system")

# =========================
# ESTILO (mantive seu CSS)
# =========================
st.markdown("""
<style>
/* ... seu CSS aqui (mantive o original) ... */
</style>
""", unsafe_allow_html=True)

# =========================
# ESTADO DA SESSÃO
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Teacher Isa. Let's practice English! How can I help you today? 🌟"}
    ]
if "nivel" not in st.session_state:
    st.session_state.nivel = "Intermediário"
if "tema" not in st.session_state:
    st.session_state.tema = "Conversação Livre"
if "processing" not in st.session_state:
    st.session_state.processing = False
if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=100)
    st.title("Teacher Isa 👩‍🏫")
    st.markdown("Your AI English Tutor")
    st.divider()
    
    st.session_state.nivel = st.selectbox(
        "🎯 Seu Nível:",
        ["Iniciante (A1-A2)", "Intermediário (B1-B2)", "Avançado (C1-C2)"],
        index=1
    )
    
    st.session_state.tema = st.selectbox(
        "📝 Foco da Aula:",
        ["Conversação Livre", "Gramática", "Vocabulário", "Preparação para Entrevista", "Inglês para Viagem"]
    )
    
    st.divider()
    
    # Upload de arquivos (Gramática extra)
    uploaded_files = st.file_uploader("📚 Enviar material (TXT/PDF):", accept_multiple_files=True)
    if uploaded_files:
        if rag_system is None:
            st.warning("RAG system não inicializado — não é possível processar documentos agora.")
        else:
            if st.button("Processar Documentos"):
                with st.spinner("Lendo material..."):
                    docs = []
                    for f in uploaded_files:
                        if f.name.lower().endswith('.txt'):
                            try:
                                docs.append(f.read().decode('utf-8'))
                            except Exception:
                                # se já for bytes/texto
                                try:
                                    docs.append(f.read().decode('utf-8', errors='ignore'))
                                except Exception:
                                    pass
                    if docs:
                        rag_system.add_documents(docs)
                        st.success("✅ Base de conhecimento atualizada!")
                    else:
                        st.warning("⚠️ Por enquanto, apenas arquivos .txt são suportados nativamente nesta versão básica.")
    
    st.divider()
    
    # Estatísticas
    if st.session_state.messages:
        num_questions = len([m for m in st.session_state.messages if m.get("role") == "user"])
        progress = min(num_questions / 10, 1.0) * 100
        
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%"></div>
        </div>
        <p style="font-size:12px; color:#6B7280; margin-top:4px;">
            {num_questions}/10 questions interacted (progress towards next milestone)
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown("**📌 Recent topics:**")
    if st.session_state.messages:
        for msg in reversed(st.session_state.messages):
            if msg.get("role") == "user":
                words = msg.get("content").split()[:8]
                st.caption("• " + " ".join(words) + "...")
                break
    else:
        st.caption("• waiting for input...")
    
    st.markdown("**📊 Statistics:**")
    total_msgs = len(st.session_state.messages)
    questions = len([m for m in st.session_state.messages if m.get("role") == "user"])
    st.caption(f"• {total_msgs} messages exchanged")
    st.caption(f"• {questions} questions asked")

# =========================
# HISTÓRICO DE CHAT
# =========================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        # use apenas role; avatar custom pode ser renderizado via markdown se quiser
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# =========================
# LÓGICA DE ENVIO DO CHAT
# =========================
user_input = st.chat_input("Type your message here...")

if user_input and not st.session_state.processing:
    st.session_state.processing = True
    st.session_state.last_user_input = user_input
    
    # 1. Adiciona a mensagem do usuário na tela
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # 2. Mostra que a IA está pensando e processa a resposta
    with st.chat_message("assistant"):
        with st.spinner("Teacher Isa is thinking..."):
            try:
                if chat_engine is None:
                    st.error("Chat engine não inicializado. Verifique logs no servidor.")
                else:
                    enriched_input = (
                        f"[Nível do aluno: {st.session_state.nivel} | "
                        f"Foco: {st.session_state.tema}]\n{user_input}"
                    )

                    # Ajuste conforme a API do seu chat_engine (chat/generate/ask)
                    # Ex.: response = chat_engine.chat(enriched_input)
                    if hasattr(chat_engine, "chat"):
                        response = chat_engine.chat(enriched_input)
                    elif hasattr(chat_engine, "complete"):
                        response = chat_engine.complete(enriched_input)
                    else:
                        response = str(chat_engine)  # fallback informativo

                    if hasattr(chat_engine, "chat"):
                        result = chat_engine.chat(enriched_input)
                        response_text = result.response if hasattr(result, "response") else str(result)

                    else:
                        st.error("❌ Teacher Isa couldn't respond right now. Try again!")
                    
            except Exception as e:
                logger.exception("Erro ao gerar resposta: %s", e)
                st.error(f"❌ Ocorreu um erro: {str(e)}")
            
            finally:
                st.session_state.processing = False
                st.rerun()