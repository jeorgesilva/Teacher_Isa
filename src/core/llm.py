"""
LLM module for Teacher Isa AI.
Handles HuggingFace Router API integration with OpenAI SDK and pedagogical prompts.
"""

import logging
import streamlit as st
from openai import OpenAI
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
    Get OpenAI client configured for HuggingFace Router.
    
    Returns:
        OpenAI: Configured OpenAI client
        
    Raises:
        StreamlitException: If API token not found in st.secrets
    """
    try:
        api_token = st.secrets.get("HUGGINGFACEHUB_API_TOKEN")
        if not api_token:
            st.error("❌ HUGGINGFACEHUB_API_TOKEN not found in st.secrets")
            st.info("💡 Add your token to `.streamlit/secrets.toml`")
            st.stop()
        
        # Create and return OpenAI client with HuggingFace Router
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=api_token,
        )
        
        logger.info("✅ HuggingFace OpenAI client initialized")
        return client
    except Exception as e:
        logger.error(f"Failed to get HuggingFace client: {str(e)}")
        st.error(f"❌ Error getting API client: {str(e)}")
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
    Generate response using LLM (via OpenAI SDK with HuggingFace Router), optionally enriched with RAG context.
    
    Args:
        messages: List of conversation messages (HumanMessage, AIMessage)
        rag_context: Optional RAG-retrieved context to include in prompt
        llm: OpenAI client (defaults to creating new client if None)
        
    Returns:
        str: Generated response from the model, or None if error occurs
    """
    try:
        if llm is None:
            llm = get_huggingface_llm()
        
        # Format messages for OpenAI API
        formatted_messages = []
        
        # Add system prompt
        formatted_messages.append({
            "role": "system",
            "content": TEACHER_ISA_SYSTEM_PROMPT
        })
        
        # Add context if RAG found documents
        if rag_context:
            formatted_messages.append({
                "role": "system",
                "content": f"[Reference Material from Knowledge Base]\n{rag_context}"
            })
        
        # Add conversation history
        for msg in messages:
            if hasattr(msg, 'content'):
                # Handle both HumanMessage/AIMessage and dict formats
                content = msg.content if isinstance(msg.content, str) else str(msg.content)
                
                if hasattr(msg, '__class__'):
                    class_name = msg.__class__.__name__
                    if 'HumanMessage' in class_name:
                        formatted_messages.append({"role": "user", "content": content})
                    elif 'AIMessage' in class_name:
                        formatted_messages.append({"role": "assistant", "content": content})
        
        # Call OpenAI API via HuggingFace Router
        logger.info("Calling OpenAI API via HuggingFace Router")
        
        response = llm.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct:novita",
            messages=formatted_messages,
            max_tokens=512,
            temperature=0.7,
            top_p=0.95,
        )
        
        # Extract response
        generated_text = response.choices[0].message.content.strip()
        
        logger.info(f"✅ Response generated (length: {len(generated_text)})")
        return generated_text
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating response: {error_msg}")
        return f"Erro ao gerar resposta: {error_msg}"


