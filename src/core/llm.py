import os
import logging
from openai import OpenAI
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv() # Carrega o .env automaticamente

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEACHER_ISA_SYSTEM_PROMPT = """You are Teacher Isa, an expert English language tutor... (mantenha todo o seu prompt aqui)"""

def get_groq_llm():
    """Inicializa o cliente OpenAI apontando para a API ultrarrápida do Groq."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY não encontrada no ambiente.")
    
    # O Groq é compatível com a biblioteca da OpenAI!
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )
    logger.info("✅ Cliente Groq inicializado")
    return client

def get_response_with_rag(messages: List[dict], rag_context: Optional[str] = None, llm = None) -> str:
    """Gera a resposta usando o Groq."""
    try:
        if llm is None:
            llm = get_groq_llm()
        
        formatted_messages = [{"role": "system", "content": TEACHER_ISA_SYSTEM_PROMPT}]
        
        if rag_context:
            formatted_messages.append({
                "role": "system",
                "content": f"[Material de Referência]\n{rag_context}"
            })
            
        formatted_messages.extend(messages)
        
        # Usando o Llama 3 70B através do Groq
        response = llm.chat.completions.create(
            model="llama3-70b-8192", 
            messages=formatted_messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=0.95,
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {str(e)}")
        raise e