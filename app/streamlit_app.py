import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# 1. Configuração de API (Lugar para eu inserir minha chave)
# [LACUNA: Configurar chave via st.secrets ou os.getenv]

# 2. Configurações da Isa (System Instructions)
SYSTEM_PROMPT = """
You are Teacher Isa, a supportive and expert English teacher. 
Your goal is to practice conversation with students. 
[LACUNA: Adicionar diretrizes específicas de correção linguística aqui]
"""

# 3. Inicialização do Modelo

def get_response(messages):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    return llm.invoke(messages)

# 4. UI Streamlit
st.set_page_config(page_title="Teacher Isa AI", page_icon="🎓")

# Sidebar
st.sidebar.title('Teacher Isa Settings')
if st.sidebar.button('Limpar Histórico'):
    st.session_state.messages = []

# Placeholder para Daily English Fact
english_facts = ["Fact 1", "Fact 2", "Fact 3"]  # Placeholder
st.sidebar.info(st.session_state.get('daily_fact', english_facts[0]))

# Chat Container
if 'messages' not in st.session_state:
    st.session_state.messages = []

# [Copilot: Desenvolva aqui a lógica de Session State para histórico de chat]
for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.chat_message('user').markdown(msg['content'])
    else:
        st.chat_message('assistant').markdown(msg['content'])

# [Copilot: Desenvolva aqui a interface de chat_input e exibição de mensagens]
user_input = st.chat_input("Digite sua mensagem...")
if user_input:
    st.session_state.messages.append({'role': 'user', 'content': user_input})
    response = get_response([HumanMessage(content=user_input), SystemMessage(content=SYSTEM_PROMPT)])
    st.session_state.messages.append({'role': 'assistant', 'content': response})
    st.experimental_rerun()

# Função para RAG

def get_grammar_reference(query):
    return ""  # TODO: Implementar FAISS/ChromaDB para busca em PDFs de gramática
