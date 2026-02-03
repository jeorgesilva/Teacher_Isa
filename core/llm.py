"""
LLM module for Teacher Isa AI.
Handles HuggingFace Inference API integration with pedagogical prompts.
"""

import logging
import streamlit as st
import requests
from langchain.schema import HumanMessage, AIMessage
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEACHER_ISA_SYSTEM_PROMPT = """You are Teacher Isa, an expert English language tutor with deep knowledge of:
- Grammar and syntax (all levels)
- Vocabulary expansion and contextual usage
- Pronunciation guidance and phonetic patterns
- Conversation practice and real-world English
- Writing improvement and style refinement

Your teaching philosophy includes:

1. **Pedagogical Recasting**: When a student makes an error, subtly correct it within your natural response 
   to preserve conversational flow. Never explicitly say "you made a mistake."
   
2. **Scaffolding**: Provide progressive hints and supportive prompts that build learner confidence. 
   Break complex concepts into manageable steps.
   
3. **Motivation**: Always be encouraging and positive. Celebrate progress, no matter how small. 
   Use inclusive language that makes learners feel supported.

4. **Contextual Learning**: Connect grammar rules to real usage. Provide examples from everyday 
   English that learners encounter in movies, books, and conversations.

5. **Personalization**: Adapt your explanations to the student's level and learning style. 
   Be concise with advanced learners, detailed with beginners.

When responding:
- Listen carefully to what the student is trying to communicate
- Identify learning needs without being explicit about errors
- Provide clear, memorable explanations
- Use analogies and real-world examples when helpful
- Ask follow-up questions to deepen understanding
- Celebrate correct usage and creative attempts

Remember: Your goal is to build the student's confidence and competence simultaneously."""


def get_huggingface_llm():
    """
    Get HuggingFace API token from secrets.
    
    Returns:
        str: API token
        
    Raises:
        StreamlitException: If API token not found in st.secrets
    """
    try:
        api_token = st.secrets.get("HUGGINGFACEHUB_API_TOKEN")
        if not api_token:
            st.error("❌ HUGGINGFACEHUB_API_TOKEN not found in st.secrets")
            st.info("💡 Add your token to `.streamlit/secrets.toml`")
            st.stop()
        
        logger.info("✅ HuggingFace API token retrieved")
        return api_token
    except Exception as e:
        logger.error(f"Failed to get HuggingFace token: {str(e)}")
        st.error(f"❌ Error getting API token: {str(e)}")
        st.stop()


def format_messages_for_llm(messages: List) -> str:
    """
    Convert LangChain message objects to formatted prompt string.
    
    Args:
        messages: List of HumanMessage and AIMessage objects
        
    Returns:
        str: Formatted prompt string for the model
    """
    formatted = TEACHER_ISA_SYSTEM_PROMPT + "\n\n---\n\n"
    
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted += f"Student: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            formatted += f"Teacher Isa: {msg.content}\n"
    
    formatted += "Teacher Isa:"
    return formatted


def get_response_with_rag(
    messages: List,
    rag_context: Optional[str] = None,
    llm = None
) -> Optional[str]:
    """
    Generate response using LLM, optionally enriched with RAG context.
    
    Args:
        messages: List of conversation messages (HumanMessage, AIMessage)
        rag_context: Optional RAG-retrieved context to include in prompt
        llm: API token string (defaults to getting from secrets if None)
        
    Returns:
        str: Generated response from the model, or None if error occurs
    """
    try:
        if llm is None:
            llm = get_huggingface_llm()
        
        # Format messages
        prompt = format_messages_for_llm(messages)
        
        # Inject RAG context if available
        if rag_context:
            prompt = prompt.replace(
                "Teacher Isa:",
                f"[Reference Material]\n{rag_context}\n\n[Response]\nTeacher Isa:"
            )
            logger.info(f"RAG context injected (length: {len(rag_context)})")
        
        # Generate response using HuggingFace Router API
        logger.info("Calling HuggingFace Router API for response generation")
        
        API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {
            "Authorization": f"Bearer {llm}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.95,
                "return_full_text": False
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract generated text
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get("generated_text", "")
        elif isinstance(result, dict):
            generated_text = result.get("generated_text", "")
        else:
            generated_text = str(result)
        
        # Clean up response
        generated_text = generated_text.strip()
        if generated_text.startswith("Teacher Isa:"):
            generated_text = generated_text.replace("Teacher Isa:", "").strip()
        
        logger.info(f"✅ Response generated (length: {len(generated_text)})")
        return generated_text
    
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error: {e}"
        if e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg = f"HTTP {e.response.status_code}: {error_detail}"
            except:
                error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
        logger.error(f"Error generating response: {error_msg}")
        return f"Erro ao gerar resposta: {error_msg}"
    
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return f"Erro inesperado: {str(e)}"

