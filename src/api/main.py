from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.core.llm import get_response_with_rag
from src.core.rag import RAGSystem

app = FastAPI(title="Teacher Isa API")
rag_system = RAGSystem() # Inicializa o RAG quando a API sobe

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    nivel: str = "Intermediário"

@app.get("/")
def read_root():
    return {"status": "A Teacher Isa está online!"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Pega a última mensagem do usuário para buscar no RAG
        user_msg = next((m.content for m in reversed(request.messages) if m.role == "user"), "")
        
        rag_context = None
        if user_msg:
            rag_context = rag_system.search_docs(user_msg, top_k=3)
            
        # Converte a lista Pydantic para a lista de dicionários que o llm.py espera
        dict_messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        # Adiciona o contexto do nível na primeira mensagem do usuário
        if dict_messages and dict_messages[-1]["role"] == "user":
            dict_messages[-1]["content"] = f"[Nível do aluno: {request.nivel}] {dict_messages[-1]['content']}"

        resposta = get_response_with_rag(dict_messages, rag_context=rag_context)
        
        return {"response": resposta, "docs_found": bool(rag_context)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))