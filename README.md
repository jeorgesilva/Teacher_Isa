# 🎓 Teacher Isa — KI‑gestützter Sprachlernassistent
![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Streamlit](https://img.shields.io/badge/Streamlit-FE4B4B?style=for-the-badge&logo=streamlit&logoColor=white)![LangChain](https://img.shields.io/badge/LangChain-6F42C1?style=for-the-badge&logo=langchain&logoColor=white) ![HuggingFace](https://img.shields.io/badge/HuggingFace-FF9900?style=for-the-badge&logo=huggingface&logoColor=white) ![ChromaDB](https://img.shields.io/badge/ChromaDB-2E8B57?style=for-the-badge) ![Sentence Transformers](https://img.shields.io/badge/Sentence--Transformers-007ACC?style=for-the-badge)

---

## Kurzbeschreibung

         Teacher Isa ist ein konversationsorientierter Tutor für Englischlernen, der NLP und Retrieval‑Augmented Generation (RAG) kombiniert.  
         System: Semantische Suche (ChromaDB) → Kontextanreicherung (RAG) → LLM‑Antwort (HuggingFace) → pädagogisch fundiertes Feedback.  
         Ziel: realitätsnahe, motivierende Übungseinheiten mit erklärenden, kontextbezogenen Rückmeldungen.
         
---

## Hauptfunktionen

         - RAG‑gestützte Antworten: semantische Suche in Referenzmaterialien zur Absicherung von Korrekturen.  
         - LLM‑Integration: HuggingFace‑Modelle (z. B. Mistral‑7B‑Instruct) für kontextuelle, mehrsprachige Antworten.  
         - Pädagogisches Design: Recasting, Scaffolding und positive Verstärkung eingebettet in natürliche Dialoge.  
         - Interaktive UI: Streamlit‑Frontend mit Chat‑Interface und Verlauf.  
         - Lokale Persistenz: ChromaDB für Embeddings und schnelle semantische Suche.  
         - Produktionsorientiert: klare Trennung von RAG, LLM‑Calls und UI; einfache Containerisierung möglich.
         
---

## Projektstruktur (empfohlen)

```
Teacher_Isa/
├── .env
├── requirements.txt
├── src/
│   ├── api/
│   │   └── main.py         # FastAPI Server (optional)
│   ├── core/
│   │   ├── llm.py          # LLM‑Adapter
│   │   └── rag.py          # ChromaDB Integration
│   └── web/
│       └── app.py          # Streamlit App
├── data/
│   └── knowledge_base/     # PDFs, Referenzen (nicht versioniert)
├── docs/
│   └── examples/
└── README.md
```

---

## Schnellstart (lokal)

1. **Klonen**

         git clone <repository-url>
         cd Teacher_Isa


2. **Secrets konfigurieren**
- Erstelle `.streamlit/secrets.toml` oder `.env` mit:
```toml
HUGGINGFACEHUB_API_TOKEN = "your_token_here"
```
**Wichtig:** Secrets niemals in Git committen.

3. **Virtuelle Umgebung & Abhängigkeiten**
```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

4. **App starten**
```bash
streamlit run src/web/app.py
```
Die App läuft standardmäßig unter `http://localhost:8501`.

---

## Outputs & Artefakte

         - Interaktive Chat‑UI (Streamlit)  
         - RAG‑Index (ChromaDB‑Ordner mit Embeddings)  
         - Logs: LLM‑Calls, RAG‑Treffer, Session‑History  
         - Optional: Exportierte Reports / Übungsprotokolle

---

## Hinweise & Best Practices

         - Datenquellen: Lade Lehrmaterialien (PDFs, Texte) lokal in `data/knowledge_base/` und indexiere sie mit ChromaDB.  
         - API‑Limits: Achte auf HuggingFace‑Token‑Limits; setze sinnvolle Fallbacks für LLM‑Ausfälle.  
         - Pädagogik: Recasting und Scaffolding sind bewusst subtil; teste mit echten Lernenden.  
         - Sicherheit: Keine sensiblen Daten in Trainings‑ oder Indexdateien; Secrets über Umgebungsvariablen verwalten.

---

## Roadmap

         - Phase 2: Knowledge base mit Grammatik‑PDFs füllen und RAG‑Relevanz optimieren.  
         - Phase 3: Performance‑Tuning (Antwortlatenz, Embedding‑Cache).  
         - Phase 4: Erweiterte Features — Speech‑to‑Text, Schreibbewertung, Lernpfade.  
         - Phase 5: Produktion — Docker, Auth, persistente DB für Konversationen.
---

## Mitwirken

- Forken, Feature‑Branch `feature/<name>` erstellen und PR gegen `main` öffnen.  
- Issues für Bugs oder Feature‑Wünsche anlegen.  
- Bitte Tests für Kernfunktionen (RAG, LLM‑Adapter) beifügen.

---

## Kontakt

**Jeorge Silva** — AI Engineer  
GitHub: `github.com/jeorgesilva`

---

## Lizenz

MIT License — Nutzung für Bildung und kommerzielle Zwecke erlaubt.

---

## Status

🚀 **Phase 1 abgeschlossen** — Kernarchitektur implementiert: Streamlit UI, HuggingFace‑Integration, ChromaDB RAG.  
⏳ **Phase 2 ausstehend** — Knowledge base mit Grammatikreferenzen befüllen und Relevanztests durchführen.
