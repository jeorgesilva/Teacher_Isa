"""
Streamlit UI for Teacher Isa AI.
Interactive English learning assistant with RAG-powered responses.
"""

import streamlit as st
import logging
from datetime import datetime
from langchain.schema import HumanMessage, AIMessage

# Import core modules
from src.core.llm import get_response_with_rag, get_huggingface_llm
from src.core.rag import rag_system

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

# =========================
# ESTILO PERSONALIZADO
# =========================
st.markdown("""
<style>
:root {
  --primary: #4A90E2;
  --accent: #7ED957;
  --bg: #F6F7FB;
  --card: #FFFFFF;
  --muted: #6B7280;
  --user-bubble: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --isa-bubble: #FFFFFF;
}

/* Importar fonte Inter */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
    background: var(--bg);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header fixo */
.header-fixed {
    position: sticky;
    top: 0;
    z-index: 100;
    background: white;
    padding: 16px 0;
    border-bottom: 1px solid #E5E7EB;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}

.header-title {
    font-size: 24px;
    font-weight: 700;
    color: var(--primary);
    display: flex;
    align-items: center;
    gap: 12px;
}

.breadcrumb {
    color: var(--muted);
    font-size: 14px;
    font-weight: 500;
}

/* Cards */
.card {
    background: var(--card);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 6px 18px rgba(20, 20, 40, 0.06);
    margin-bottom: 16px;
    border: 1px solid #F0F0F0;
}

/* Chat bubbles melhoradas */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 16px 0;
}

.message-wrapper {
    display: flex;
    gap: 12px;
    animation: fadeIn 0.3s ease-in;
}

.message-wrapper.user {
    flex-direction: row-reverse;
}

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.avatar.user-avatar {
    background: var(--user-bubble);
}

.avatar.isa-avatar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.chat-bubble-user {
    background: var(--user-bubble);
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    max-width: 70%;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
    font-size: 15px;
    line-height: 1.5;
}

.chat-bubble-isa {
    background: var(--isa-bubble);
    border: 1px solid #E5E7EB;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    max-width: 70%;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    font-size: 15px;
    line-height: 1.6;
    color: #1F2937;
}

.message-meta {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-top: 4px;
    padding: 0 4px;
}

.timestamp {
    color: var(--muted);
    font-size: 12px;
    font-weight: 500;
}

.copy-btn {
    color: var(--muted);
    font-size: 12px;
    cursor: pointer;
    opacity: 0.6;
    transition: opacity 0.2s;
}

.copy-btn:hover {
    opacity: 1;
}

/* Chips para ações rápidas */
.chip-container {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 16px 0;
}

.chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    border-radius: 24px;
    background: white;
    border: 1.5px solid #E5E7EB;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    color: #374151;
    transition: all 0.2s;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}

.chip:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(74, 144, 226, 0.15);
    transform: translateY(-2px);
}

.chip-icon {
    font-size: 16px;
}

/* Painel de status */
.status-panel {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 8px 0;
    font-size: 14px;
    font-weight: 500;
}

.status-icon {
    font-size: 18px;
}

/* Progress bar */
.progress-container {
    background: #E5E7EB;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin: 12px 0;
}

.progress-bar {
    background: var(--accent);
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

/* Sidebar melhorada */
.sidebar-section {
    margin-bottom: 24px;
}

.sidebar-title {
    font-size: 16px;
    font-weight: 700;
    color: #1F2937;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Upload preview */
.upload-preview {
    background: #F9FAFB;
    border: 2px dashed #D1D5DB;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    margin: 12px 0;
}

/* Animações */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.typing-indicator {
    display: flex;
    gap: 4px;
    padding: 12px 16px;
}

.typing-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--muted);
    animation: pulse 1.4s infinite;
}

.typing-dot:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
    animation-delay: 0.4s;
}

/* Responsividade */
@media (max-width: 768px) {
    .chat-bubble-user,
    .chat-bubble-isa {
        max-width: 85%;
    }
    
    .chip {
        font-size: 13px;
        padding: 8px 12px;
    }
}

/* Scrollbar personalizado */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #F3F4F6;
}

::-webkit-scrollbar-thumb {
    background: #D1D5DB;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #9CA3AF;
}
</style>
""", unsafe_allow_html=True)

# =========================
# ESTADO DA SESSÃO
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
    logger.info("Initialized new chat session")

if "rag_logs" not in st.session_state:
    st.session_state.rag_logs = []

if "llm" not in st.session_state:
    st.session_state.llm = None

if "nivel" not in st.session_state:
    st.session_state.nivel = "Intermediário"

if "keywords" not in st.session_state:
    st.session_state.keywords = []

if "processing" not in st.session_state:
    st.session_state.processing = False

if "last_user_input" not in st.session_state:
    st.session_state.last_user_input = ""


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="sidebar-title">📚 Teacher Isa</h2>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">🎯 Configurações</p>', unsafe_allow_html=True)

    nivel = st.selectbox(
        "Nível de explicação",
        ["Básico", "Intermediário", "Avançado", "Prática"],
        index=["Básico", "Intermediário", "Avançado", "Prática"].index(st.session_state.nivel)
    )
    st.session_state.nivel = nivel

    temperature = st.slider(
        "Criatividade",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Menor = mais focado, Maior = mais criativo"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # Upload de arquivos
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">📁 Material de Apoio</p>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Envie PDFs, imagens ou textos",
        type=["pdf", "png", "jpg", "jpeg", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")
        for f in uploaded_files[:3]:  # Mostrar primeiros 3
            st.caption(f"📄 {f.name}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # RAG Logs
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-title">🔍 Histórico de Buscas</p>', unsafe_allow_html=True)
    if st.session_state.rag_logs:
        with st.expander(f"Ver {len(st.session_state.rag_logs)} buscas", expanded=False):
            for i, log in enumerate(reversed(st.session_state.rag_logs[-5:]), 1):
                status = "✅" if log.get("docs_found") else "❌"
                query_short = log.get("query", "")[:40]
                st.caption(f'{status} {query_short}...')
    else:
        st.caption("Nenhuma busca ainda")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # System Status com card
    st.markdown('<div class="status-panel">', unsafe_allow_html=True)
    st.markdown('<p style="font-size:14px; font-weight:600; margin-bottom:8px;">🔧 Status do Sistema</p>', unsafe_allow_html=True)
    try:
        llm = get_huggingface_llm()
        st.markdown('<div class="status-item"><span class="status-icon">✅</span> LLM Conectado</div>', unsafe_allow_html=True)
    except Exception as e:
        st.markdown('<div class="status-item"><span class="status-icon">❌</span> Erro LLM</div>', unsafe_allow_html=True)
    
    if rag_system:
        st.markdown('<div class="status-item"><span class="status-icon">✅</span> RAG Pronto</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-item"><span class="status-icon">⚠️</span> RAG Indisponível</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    st.caption("Teacher Isa AI © 2026")
    st.caption("Powered by HuggingFace & ChromaDB")

# =========================
# TÍTULO PRINCIPAL COM HEADER FIXO
# =========================
st.markdown("""
<div class="header-fixed">
    <div class="header-content">
        <div class="header-title">
            👩‍🏫 Teacher Isa
            <span style="font-size:14px; font-weight:500; color:#6B7280;">— Seu professor digital</span>
        </div>
        <div class="breadcrumb">
            Nível: <strong>{}</strong> • {} mensagens
        </div>
    </div>
</div>
""".format(
    st.session_state.nivel,
    len(st.session_state.messages)
), unsafe_allow_html=True)

# =========================
# ÁREA PRINCIPAL EM DUAS COLUNAS
# =========================
col_chat, col_tools = st.columns([2, 1])

# =========================
# COLUNA DO CHAT
# =========================
with col_chat:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin:0 0 16px 0; font-size:18px; font-weight:600; color:#1F2937;">💬 Conversa</h3>', unsafe_allow_html=True)

    # Mostrar histórico com avatares e timestamps
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        timestamp = datetime.now().strftime("%H:%M")
        
        if isinstance(msg, HumanMessage):
            st.markdown(f"""
            <div class="message-wrapper user">
                <div class="avatar user-avatar">👤</div>
                <div>
                    <div class="chat-bubble-user">{msg.content}</div>
                    <div class="message-meta">
                        <span class="timestamp">{timestamp}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif isinstance(msg, AIMessage):
            st.markdown(f"""
            <div class="message-wrapper">
                <div class="avatar isa-avatar">👩‍🏫</div>
                <div>
                    <div class="chat-bubble-isa">{msg.content}</div>
                    <div class="message-meta">
                        <span class="timestamp">{timestamp}</span>
                        <span class="copy-btn" title="Copiar">📋</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Entrada do usuário
    user_input = st.chat_input(
        "Digite sua pergunta ou dúvida..."
    )

    if user_input and not st.session_state.processing:
        # Previne múltiplos processamentos
        st.session_state.processing = True
        st.session_state.last_user_input = user_input
        
        # Adiciona mensagem do usuário
        st.session_state.messages.append(HumanMessage(content=user_input))
        logger.info(f"User input: {user_input[:50]}...")
        
        # Mostrar indicador de digitação
        st.markdown("""
        <div class="message-wrapper">
            <div class="avatar isa-avatar">👩‍🏫</div>
            <div class="chat-bubble-isa">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.spinner("🤔 Teacher Isa está pensando..."):
            try:
                # Perform RAG search
                rag_context = None
                if rag_system:
                    rag_context = rag_system.search_docs(user_input, top_k=3)
                    st.session_state.rag_logs.append({
                        "query": user_input,
                        "docs_found": bool(rag_context),
                        "timestamp": datetime.now().isoformat()
                    })
                    logger.info(f"RAG context found: {bool(rag_context)}")
                
                # Get LLM response
                llm = st.session_state.llm or get_huggingface_llm()
                st.session_state.llm = llm
                
                # Add nivel to context
                context_prompt = f"Nível do aluno: {st.session_state.nivel}. "
                full_messages = st.session_state.messages.copy()
                if full_messages and isinstance(full_messages[0], HumanMessage):
                    full_messages[0] = HumanMessage(content=context_prompt + full_messages[0].content)
                
                response = get_response_with_rag(
                    full_messages,
                    rag_context=rag_context,
                    llm=llm
                )
                
                if response:
                    # Add AI response to history
                    st.session_state.messages.append(AIMessage(content=response))
                    logger.info(f"Response generated: {response[:50]}...")
                else:
                    st.error("❌ Falha ao gerar resposta. Tente novamente.")
            
            except Exception as e:
                logger.error(f"Error in chat processing: {str(e)}")
                st.error(f"❌ Erro: {str(e)}")
            
            finally:
                # Libera o processamento para próxima mensagem
                st.session_state.processing = False
                st.rerun()

# =========================
# COLUNA DE FERRAMENTAS
# =========================
with col_tools:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin:0 0 16px 0; font-size:18px; font-weight:600; color:#1F2937;">⚡ Ações Rápidas</h3>', unsafe_allow_html=True)

    # Grid de botões 2x2
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Resumo", use_container_width=True, key="btn_resumo"):
            if st.session_state.messages:
                last_msg = st.session_state.messages[-1]
                if isinstance(last_msg, AIMessage):
                    st.info("💡 **Resumo:** " + last_msg.content[:200] + "...")
            else:
                st.warning("Inicie uma conversa primeiro!")
    
    with col2:
        if st.button("🎯 Quiz", use_container_width=True, key="btn_quiz"):
            st.info("🎯 **Quiz:** (em desenvolvimento)")

    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("💡 Exemplos", use_container_width=True, key="btn_exemplos"):
            if st.session_state.last_user_input:
                st.session_state.messages.append(HumanMessage(
                    content=f"Me dê 3 exemplos práticos sobre: {st.session_state.last_user_input}"
                ))
                st.session_state.processing = False
                st.rerun()
            else:
                st.warning("Digite uma pergunta primeiro!")
    
    with col4:
        if st.button("🎨 Analogia", use_container_width=True, key="btn_analogia"):
            if st.session_state.messages:
                last_user_msg = None
                for msg in reversed(st.session_state.messages):
                    if isinstance(msg, HumanMessage):
                        last_user_msg = msg.content
                        break
                if last_user_msg:
                    st.session_state.messages.append(HumanMessage(
                        content=f"Crie uma analogia simples para explicar: {last_user_msg}"
                    ))
                    st.session_state.processing = False
                    st.rerun()
            else:
                st.warning("Inicie uma conversa primeiro!")
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")
    
    # Painel de apoio
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 style="margin:0 0 16px 0; font-size:18px; font-weight:600; color:#1F2937;">🧠 Painel de Apoio</h3>', unsafe_allow_html=True)
    
    # Progresso de aprendizagem
    if st.session_state.messages:
        num_questions = len([m for m in st.session_state.messages if isinstance(m, HumanMessage)])
        progress = min(num_questions / 10, 1.0) * 100
        
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%"></div>
        </div>
        <p style="font-size:12px; color:#6B7280; margin-top:4px;">
            {num_questions}/10 perguntas nesta sessão
        </p>
        """, unsafe_allow_html=True)
    
    st.markdown("**📌 Tópico atual:**")
    if st.session_state.messages:
        for msg in reversed(st.session_state.messages):
            if isinstance(msg, HumanMessage):
                words = msg.content.split()[:8]
                st.caption("• " + " ".join(words) + "...")
                break
    else:
        st.caption("• Aguardando primeira pergunta...")
    
    st.markdown("**📊 Estatísticas:**")
    total_msgs = len(st.session_state.messages)
    questions = len([m for m in st.session_state.messages if isinstance(m, HumanMessage)])
    st.caption(f"• {total_msgs} mensagens trocadas")
    st.caption(f"• {questions} perguntas feitas")
    
    if uploaded_files:
        st.markdown("**📁 Arquivos:**")
        for f in uploaded_files[:3]:
            st.caption(f"• {f.name}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.divider()
st.caption("Teacher Isa AI © 2026 | Powered by HuggingFace & ChromaDB")

