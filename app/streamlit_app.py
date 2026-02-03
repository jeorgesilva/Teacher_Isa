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

# Page configuration
st.set_page_config(
    page_title="Teacher Isa AI",
    page_icon="👩‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .student-message {
        background-color: #e3f2fd;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #2196f3;
    }
    .teacher-message {
        background-color: #f3e5f5;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #9c27b0;
    }
    .rag-log-item {
        background-color: #f5f5f5;
        padding: 8px 12px;
        border-radius: 6px;
        margin: 4px 0;
        font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    logger.info("Initialized new chat session")

if "rag_logs" not in st.session_state:
    st.session_state.rag_logs = []

if "llm" not in st.session_state:
    st.session_state.llm = None

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Temperature slider
    temperature = st.slider(
        "Response Temperature (0=deterministic, 1=creative)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower = more focused, Higher = more creative"
    )
    
    # Daily English Fact
    st.subheader("📚 Daily English Fact")
    facts = [
        "The word 'set' has over 430 definitions in English!",
        "English has no official national body to regulate it.",
        "'Dreamt' is the only English word that ends in 'mt'.",
        "The letter 'E' is the most commonly used letter in English.",
        "'Uncopyrightable' is the longest English word with no repeated letters.",
        "The word 'queue' is pronounced the same as its first letter 'Q'.",
        "'Almost' is the longest English word with all letters in alphabetical order.",
    ]
    import random
    st.info(f"💡 {random.choice(facts)}")
    
    # RAG Logs
    st.subheader("🔍 RAG Search Logs")
    if st.session_state.rag_logs:
        with st.expander(f"View {len(st.session_state.rag_logs)} searches"):
            for i, log in enumerate(reversed(st.session_state.rag_logs[-10:]), 1):
                status = "✅ Found docs" if log.get("docs_found") else "❌ No docs"
                st.markdown(
                    f'<div class="rag-log-item">{i}. "{log.get("query", "")[:50]}..." {status}</div>',
                    unsafe_allow_html=True
                )
    else:
        st.caption("No searches yet")
    
    # System Status
    st.subheader("🔧 System Status")
    try:
        llm = get_huggingface_llm()
        st.success("✅ LLM Connected")
    except Exception as e:
        st.error(f"❌ LLM Error: {str(e)[:50]}")
    
    if rag_system:
        st.success("✅ RAG System Ready")
    else:
        st.warning("⚠️ RAG System Not Available")

# Main chat interface
st.title("👩‍🏫 Teacher Isa AI")
st.caption("Your personalized English learning assistant powered by AI")

# Chat display container
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            st.markdown(
                f'<div class="student-message"><b>You:</b> {message.content}</div>',
                unsafe_allow_html=True
            )
        elif isinstance(message, AIMessage):
            st.markdown(
                f'<div class="teacher-message"><b>Teacher Isa:</b> {message.content}</div>',
                unsafe_allow_html=True
            )

# Input section
st.divider()
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Your message:",
        placeholder="Ask about grammar, practice conversation, or anything about English...",
        label_visibility="collapsed"
    )

with col2:
    submit_button = st.button("Send 📤", use_container_width=True)

# Process user input
if user_input and (submit_button or user_input):
    # Add user message to history
    st.session_state.messages.append(HumanMessage(content=user_input))
    logger.info(f"User input: {user_input[:50]}...")
    
    with st.spinner("🤔 Teacher Isa is thinking..."):
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
            
            response = get_response_with_rag(
                st.session_state.messages,
                rag_context=rag_context,
                llm=llm
            )
            
            if response:
                # Add AI response to history
                st.session_state.messages.append(AIMessage(content=response))
                logger.info(f"Response generated: {response[:50]}...")
                st.rerun()
            else:
                st.error("❌ Failed to generate response. Please try again.")
        
        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}")
            st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.divider()
st.caption("Teacher Isa AI © 2025 | Powered by HuggingFace Inference API & ChromaDB")
