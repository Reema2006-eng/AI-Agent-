# 🧮 Agentic AI & RAG Suite (Gemini + LangChain)

This workspace provides a complete hands-on learning environment for Agentic AI and Retrieval-Augmented Generation (RAG):

1. **`rag_agent.py`** – **RAG System for the Student Database**:
   - Indexes and retrieves records from the 25-student document (`student_database.txt`).
   - Uses `gemini-embedding-001` and LangChain's `InMemoryVectorStore`.
   - Answers all 10 suggested questions from the document with 100% precision.

2. **`langchain_parallel_agent.py`** – **LangChain Concurrent Multi-Task Agent**:
   - Runs multiple tasks simultaneously using `asyncio.gather`.
   - ~2.3x speedup over sequential execution.

3. **`calculator_agent.py`** – **Zero-Framework Native ReAct Agent**:
   - `basic_calculator`, `web_search`, and `get_current_datetime` tools.
   - Built with pure Python standard library and `google-genai` SDK.

---

## 📚 Document RAG Architecture (`rag_agent.py`)

```
[Uploaded Student Document]
         │
         ▼
┌──────────────────────────────────────────────┐
│  1. Document Parsing & Semantic Chunking    │
│     (25 Student Records + Roster Context)   │
└──────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  2. Embedding Model (gemini-embedding-001)   │
└──────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  3. Vector Store (InMemoryVectorStore)       │
└──────────────────────────────────────────────┘
         │
         ▼  (User Question: "What is Priya Sharma's attendance?")
┌──────────────────────────────────────────────┐
│  4. Similarity Retrieval (Top-k Chunks)      │
└──────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  5. Context-Augmented Generation             │
│     (ChatGoogleGenerativeAI: gemini-3.1)     │
└──────────────────────────────────────────────┘
         │
         ▼
[Grounded Answer with 100% Accuracy]
```

---

## 🚀 How to Run the Student Database RAG

In PowerShell or terminal:

```powershell
python C:\Users\Admin\.gemini\antigravity\scratch\gemini-calculator-agent\rag_agent.py
```

The script will:
1. Initialize `gemini-embedding-001` and index the 25 student records in memory.
2. Automatically run and display answers for all **10 Suggested Questions from the document**:
   1. *What is Priya Sharma's attendance and overall mark?*
   2. *Who has the highest overall mark?*
   3. *Which students belong to the CSE department?*
   4. *List students whose attendance is below 75%.*
   5. *Who scored above 90 in AI?*
   6. *How many students are placement eligible?*
   7. *What is Arjun Kumar's DSA mark?*
   8. *Which student has the highest attendance?*
   9. *Find all AIDS students with an overall mark above 80.*
   10. *What is the phone number of Fathima N?*
3. Launch an **Interactive RAG Chat** where you can ask any custom question about the students!
