"""
Streamlit UI for Teacher Isa AI.
Interactive English learning assistant with RAG-powered responses.
"""

import streamlit as st
import logging
from datetime import datetime
from langchain.schema import HumanMessage, AIMessage

# Import core modules
from core.llm import get_response_with_rag, get_huggingface_llm
from core.rag import rag_system

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
.chat-bubble-user {
    background-color: #DCF8C6;
    padding: 10px 15px;
    border-radius: 10px;
    margin-bottom: 8px;
    width: fit-content;
}
.chat-bubble-isa {
    background-color: #E8EAF6;
    padding: 10px 15px;
    border-radius: 10px;
    margin-bottom: 8px;
    width: fit-content;
}
.quick-action-btn {
    background-color: #f0f0f0;
    padding: 8px 12px;
    border-radius: 6px;
    margin: 4px 0;
    cursor: pointer;
}
.info-panel {
    background-color: #f9f9f9;
    padding: 12px;
    border-radius: 8px;
    margin: 8px 0;
    border-left: 3px solid #4CAF50;
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


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.title("📚 Teacher Isa")
    st.subheader("Configurações de Aprendizagem")

    nivel = st.selectbox(
        "Nível de explicação",
        ["Básico", "Intermediário", "Avançado", "Prática"],
        index=["Básico", "Intermediário", "Avançado", "Prática"].index(st.session_state.nivel)
    )
    st.session_state.nivel = nivel

    temperature = st.slider(
        "Criatividade da resposta",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Menor = mais focado, Maior = mais criativo"
    )

    st.markdown("---")
    st.subheader("Material de Apoio")
    uploaded_files = st.file_uploader(
        "Envie PDFs, imagens ou textos",
        type=["pdf", "png", "jpg", "jpeg", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")

    st.markdown("---")
    
    # RAG Logs
    st.subheader("🔍 Buscas RAG")
    if st.session_state.rag_logs:
        with st.expander(f"Ver {len(st.session_state.rag_logs)} buscas"):
            for i, log in enumerate(reversed(st.session_state.rag_logs[-10:]), 1):
                status = "✅ Docs" if log.get("docs_found") else "❌ Vazio"
                st.caption(f'{i}. "{log.get("query", "")[:30]}..." {status}')
    else:
        st.caption("Nenhuma busca ainda")
    
    st.markdown("---")
    
    # System Status
    st.subheader("🔧 Status do Sistema")
    try:
        llm = get_huggingface_llm()
        st.success("✅ LLM Conectado")
    except Exception as e:
        st.error(f"❌ Erro LLM: {str(e)[:30]}")
    
    if rag_system:
        st.success("✅ RAG Pronto")
    else:
        st.warning("⚠️ RAG Indisponível")
    
    st.markdown("---")
    st.caption("Versão 2.0 • HuggingFace + ChromaDB")

# =========================
# TÍTULO PRINCIPAL
# =========================
st.title("👩‍🏫 Teacher Isa — Seu professor digital")
st.write("Aprenda qualquer assunto com explicações claras, exemplos e exercícios gerados automaticamente.")

# =========================
# ÁREA PRINCIPAL EM DUAS COLUNAS
# =========================
col_chat, col_tools = st.columns([2, 1])

# =========================
# COLUNA DO CHAT
# =========================
with col_chat:
    st.subheader("💬 Conversa")

    # Mostrar histórico
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            st.markdown(
                f"<div class='chat-bubble-user'><b>Você:</b> {msg.content}</div>",
                unsafe_allow_html=True
            )
        elif isinstance(msg, AIMessage):
            st.markdown(
                f"<div class='chat-bubble-isa'><b>Teacher Isa:</b> {msg.content}</div>",
                unsafe_allow_html=True
            )

    # Entrada do usuário
    user_input = st.text_input(
        "Digite sua pergunta ou dúvida:",
        placeholder="Pergunte sobre gramática, vocabulário, conversação...",
        key="user_input"
    )

    if user_input:
        # Adiciona mensagem do usuário
        st.session_state.messages.append(HumanMessage(content=user_input))
        logger.info(f"User input: {user_input[:50]}...")
        
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
                    st.rerun()
                else:
                    st.error("❌ Falha ao gerar resposta. Tente novamente.")
            
            except Exception as e:
                logger.error(f"Error in chat processing: {str(e)}")
                st.error(f"❌ Erro: {str(e)}")

# =========================
# COLUNA DE FERRAMENTAS
# =========================
with col_tools:
    st.subheader("⚡ Ações Rápidas")

    if st.button("📝 Gerar resumo", use_container_width=True):
        if st.session_state.messages:
            last_msg = st.session_state.messages[-1]
            if isinstance(last_msg, AIMessage):
                st.info("💡 **Resumo:** " + last_msg.content[:200] + "...")
        else:
            st.warning("Inicie uma conversa primeiro!")

    if st.button("🎯 Criar quiz", use_container_width=True):
        st.info("🎯 **Quiz:** (funcionalidade em desenvolvimento)")

    if st.button("💡 Explicar com exemplos", use_container_width=True):
        if user_input:
            st.session_state.messages.append(HumanMessage(
                content=f"Me dê 3 exemplos práticos sobre: {user_input}"
            ))
            st.rerun()
        else:
            st.warning("Digite uma pergunta primeiro!")

    if st.button("🎨 Criar analogia", use_container_width=True):
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
                st.rerun()
        else:
            st.warning("Inicie uma conversa primeiro!")

    st.markdown("---")
    st.subheader("🧠 Painel de Apoio")
    
    # Palavras-chave (extraídas do último tópico)
    if st.session_state.messages:
        st.markdown("**📌 Tópico atual:**")
        for msg in reversed(st.session_state.messages):
            if isinstance(msg, HumanMessage):
                words = msg.content.split()[:5]
                st.caption(" • " + " ".join(words) + "...")
                break
    else:
        st.caption("• Aguardando primeira pergunta...")
    
    st.markdown("**📊 Estatísticas:**")
    st.caption(f"• {len(st.session_state.messages)} mensagens trocadas")
    st.caption(f"• {len([m for m in st.session_state.messages if isinstance(m, HumanMessage)])} perguntas feitas")
    
    if uploaded_files:
        st.markdown("**📁 Arquivos carregados:**")
        for f in uploaded_files:
            st.caption(f"• {f.name}")

# =========================
# FOOTER
# =========================
st.divider()
st.caption("Teacher Isa AI © 2025 | Powered by HuggingFace Inference API & ChromaDB")

