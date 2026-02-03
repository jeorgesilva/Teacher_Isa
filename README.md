# Teacher Isa AI

An AI-Driven Language Learning Assistant that blends NLP and Retrieval-Augmented Generation (RAG) to provide accurate, motivating English practice.

## Project Overview
Teacher Isa is a modern, portfolio-grade conversational tutor focused on real-world language practice. It uses semantic retrieval to ground responses in grammar references and then generates supportive, contextual feedback tailored to each learner.

## Linguistic Foundation
The system is explicitly designed around:
- **Pedagogical Recasting**: subtle correction within natural responses to preserve flow.
- **Scaffolding**: progressive hints and supportive prompts that build learner confidence.

## Tech Stack
- Python
- Streamlit
- LangChain
- Gemini Pro
- Sentence-Transformers

## Architecture Diagram (Text)

User Input
  │
  ▼
Semantic Search (RAG)
  │
  ▼
LLM Context
  │
  ▼
Pedagogical Response

## Proposed Project Structure

app/
  └─ Streamlit UI
core/
  └─ LLM, prompts, and RAG logic
data/
  └─ knowledge_base/
tests/
  └─ unit tests

## Getting Started
1. Create a .env file and add your Google API key.
2. Install dependencies from requirements.txt.
3. Run the Streamlit app.

## Environment Variables
- GOOGLE_API_KEY

## Status
This repository is undergoing a focused rebranding and architectural reset to a Streamlit + RAG foundation.
4. ✅ Test with admin commands like `/health`
5. ✅ Deploy to production server for 24/7 operation

