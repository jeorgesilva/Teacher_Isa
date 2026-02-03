# Teacher Isa AI

An AI-Driven Language Learning Assistant that blends NLP and Retrieval-Augmented Generation (RAG) to provide accurate, motivating English practice powered by open-source models.

## Project Overview

Teacher Isa is a modern, portfolio-grade conversational tutor focused on real-world English learning. It uses:
- **Semantic Retrieval (RAG)** to ground responses in grammar references
- **Large Language Models** from HuggingFace for intelligent, contextual responses
- **Pedagogical Design** principles to maximize learning outcomes

The system generates supportive, contextual feedback tailored to each learner's level and needs.

## Linguistic Foundation

The system is explicitly designed around **proven pedagogical techniques**:

1. **Pedagogical Recasting**: Subtle error correction embedded in natural responses to preserve conversational flow and learner confidence.
2. **Scaffolding**: Progressive hints and supportive prompts that build learner independence step-by-step.
3. **Positive Reinforcement**: Consistent celebration of effort and progress to maintain motivation.
4. **Contextual Learning**: Real-world English examples from movies, literature, and authentic conversations.

## Tech Stack

- **Frontend**: Streamlit 1.53.1 (interactive web UI)
- **LLM Provider**: HuggingFace Inference API (free tier)
- **LLM Model**: Mistral-7B-Instruct-v0.2 (lightweight, multilingual)
- **Framework**: LangChain 0.1.20 (orchestration)
- **Embeddings**: Sentence-Transformers 3.0.1 (semantic understanding)
- **Vector Database**: ChromaDB 0.4.24 (local persistence)
- **Runtime**: Python 3.9+

## Architecture Diagram

```
┌─────────────────┐
│  User Input     │
│  (Streamlit UI) │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│  ChromaDB Search │
│  (Semantic RAG)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│ HuggingFace LLM Context  │
│ (Mistral-7B-Instruct)    │
└────────┬─────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Pedagogical Response        │
│ (Recasting + Scaffolding)   │
└─────────────────────────────┘
```

## Project Structure

```
lucia-bot/
├── app/
│   ├── __init__.py
│   └── streamlit_app.py        # Main Streamlit UI
├── core/
│   ├── __init__.py
│   ├── llm.py                  # HuggingFace LLM integration
│   └── rag.py                  # RAG system with ChromaDB
├── data/
│   └── knowledge_base/         # Grammar reference PDFs (Phase 2)
├── tests/
│   └── __init__.py
├── requirements.txt            # Dependencies
├── .env.example                # Environment variables template
├── .streamlit/
│   └── secrets.toml            # API credentials (git-ignored)
└── README.md                   # This file
```

## Getting Started

### 1. Clone and Setup
```bash
git clone <repository-url>
cd lucia-bot
```

### 2. Get HuggingFace API Token
1. Sign up at [https://huggingface.co](https://huggingface.co)
2. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
3. Create a new token with "read" permission

### 3. Configure Secrets
Create `.streamlit/secrets.toml`:
```toml
HUGGINGFACEHUB_API_TOKEN = "your_token_here"
```

**Important**: Never commit `.streamlit/secrets.toml` to git!

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the App
```bash
streamlit run app/streamlit_app.py
```

The app will open at `http://localhost:8501`

## Features

✅ **Interactive Chat Interface**
- Real-time conversation with Teacher Isa
- Message history preservation
- Responsive Streamlit UI

✅ **RAG-Powered Responses**
- Semantic search through grammar references
- Context-aware corrections and explanations
- Invisible logging of document usage

✅ **Pedagogical Intelligence**
- Automatic recasting of errors
- Scaffolded learning progression
- Encouraging, supportive tone

✅ **Open Source**
- No API quotas or paywall
- Free HuggingFace Inference API
- Local-first ChromaDB storage

## Roadmap (Phase 2+)

- [ ] **Phase 2**: Load grammar reference PDFs into ChromaDB
  - Parse English grammar textbooks
  - Embed and index grammar rules
  - Test semantic search accuracy

- [ ] **Phase 3**: Performance Optimization
  - Benchmark LLM response times
  - Optimize RAG relevance
  - Fine-tune temperature and sampling

- [ ] **Phase 4**: Advanced Features
  - Speech-to-text input (pronunciation)
  - Writing evaluation and scoring
  - Personalized learning paths
  - Progress tracking and analytics

- [ ] **Phase 5**: Production Deployment
  - Docker containerization
  - Cloud deployment (Streamlit Cloud, Google Cloud, etc.)
  - Authentication and user management
  - Database for conversation history

## Environment Variables

```
HUGGINGFACEHUB_API_TOKEN     # HuggingFace API token (required)
```

## Development Notes

### Logging
- Backend operations logged to console
- RAG searches logged invisibly (visible in sidebar)
- LLM calls tracked for debugging

### Error Handling
- Graceful fallback if RAG documents not found
- Clear error messages for API token issues
- Session recovery on LLM timeouts

### Performance
- ChromaDB stores locally (no external API calls)
- Sentence-Transformers embeddings cached
- Message history kept in session memory

## Contributing

This is a portfolio project demonstrating:
- RAG architecture implementation
- LangChain orchestration
- Streamlit application design
- Pedagogical AI system design
- Production-ready Python code patterns

Feel free to fork, modify, and deploy!

## License

MIT License - Educational and commercial use permitted

## Status

🚀 **Phase 1 Complete**: Core architecture with HuggingFace Inference API
- ✅ Streamlit UI implemented
- ✅ HuggingFace LLM integration complete
- ✅ ChromaDB RAG system ready
- ✅ Pedagogical prompts configured

⏳ **Phase 2 Pending**: Knowledge base population with grammar references
- ⏳ Add English grammar PDFs
- ⏳ Parse and embed documents
- ⏳ Test semantic search

