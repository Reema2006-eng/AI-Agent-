"""
================================================================================
📚 RAG (RETRIEVAL-AUGMENTED GENERATION) STUDENT DATABASE AGENT
================================================================================
This script implements a complete LangChain RAG pipeline to retrieve and answer
questions from the "Dummy Student Database" document.

Key RAG Components:
1. Document Parsing & Semantic Chunking (LangChain Document objects)
2. Embeddings Model: Google Generative AI (gemini-embedding-001)
3. Vector Store: InMemoryVectorStore (Zero extra C++ dependencies/servers)
4. Context-Augmented QA Chain (LCEL: Prompt -> Retriever -> Gemini -> Parser)
5. Suggested Question Suite (Pre-evaluates the 10 questions from the PDF)
================================================================================
"""

import os
import sys
import time
import json
from typing import List, Dict, Any

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings


# ==============================================================================
# 🔑 1. API KEY & MODEL CONFIGURATION
# ==============================================================================
GEMINI_API_KEY = "AQ.Ab8RN6K3LjjcHncksHwvl7PZoDQGXne689SXNB0CW4dp0L_Ahg"

LLM_MODEL = "gemini-3.1-flash-lite"
EMBEDDING_MODEL = "gemini-embedding-001"


def get_active_api_key() -> str:
    """Retrieves Gemini API key from script variable, environment, or prompt."""
    global GEMINI_API_KEY
    if GEMINI_API_KEY and GEMINI_API_KEY.strip() and GEMINI_API_KEY.strip() != "YOUR_GEMINI_API_KEY_HERE":
        return GEMINI_API_KEY.strip()

    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    print("\n[!] No GEMINI_API_KEY found.")
    entered = input("Please paste your Gemini AI Studio API Key: ").strip()
    if not entered:
        print("[Error] An API key is required. Exiting.")
        sys.exit(1)
    return entered


# ==============================================================================
# 📄 2. DOCUMENT DATA EXTRACTION (FROM THE PDF)
# ==============================================================================
STUDENTS_DATA = [
    {"id": "STU001", "name": "Arjun Kumar", "dept": "CSE", "year": "2nd", "email": "arjun@example.com", "phone": "9000000001", "attendance": "87%", "python": 82, "dsa": 76, "ai": 91, "overall": 83, "placement": "Eligible"},
    {"id": "STU002", "name": "Priya Sharma", "dept": "IT", "year": "2nd", "email": "priya@example.com", "phone": "9000000002", "attendance": "92%", "python": 91, "dsa": 88, "ai": 94, "overall": 91, "placement": "Eligible"},
    {"id": "STU003", "name": "Rahul Raj", "dept": "ECE", "year": "2nd", "email": "rahul@example.com", "phone": "9000000003", "attendance": "74%", "python": 68, "dsa": 72, "ai": 79, "overall": 73, "placement": "Not Eligible"},
    {"id": "STU004", "name": "Sneha Devi", "dept": "CSE", "year": "2nd", "email": "sneha@example.com", "phone": "9000000004", "attendance": "95%", "python": 88, "dsa": 92, "ai": 96, "overall": 92, "placement": "Eligible"},
    {"id": "STU005", "name": "Vikram Singh", "dept": "AIDS", "year": "2nd", "email": "vikram@example.com", "phone": "9000000005", "attendance": "81%", "python": 75, "dsa": 81, "ai": 84, "overall": 80, "placement": "Eligible"},
    {"id": "STU006", "name": "Divya S", "dept": "IT", "year": "2nd", "email": "divya@example.com", "phone": "9000000006", "attendance": "89%", "python": 84, "dsa": 79, "ai": 88, "overall": 84, "placement": "Eligible"},
    {"id": "STU007", "name": "Karthik M", "dept": "EEE", "year": "2nd", "email": "karthik@example.com", "phone": "9000000007", "attendance": "69%", "python": 72, "dsa": 65, "ai": 70, "overall": 69, "placement": "Not Eligible"},
    {"id": "STU008", "name": "Aishwarya R", "dept": "CSE", "year": "2nd", "email": "aishwarya@example.com", "phone": "9000000008", "attendance": "91%", "python": 95, "dsa": 89, "ai": 93, "overall": 92, "placement": "Eligible"},
    {"id": "STU009", "name": "Mohammed Faiz", "dept": "IT", "year": "2nd", "email": "faiz@example.com", "phone": "9000000009", "attendance": "85%", "python": 78, "dsa": 86, "ai": 81, "overall": 82, "placement": "Eligible"},
    {"id": "STU010", "name": "Keerthana P", "dept": "ECE", "year": "2nd", "email": "keerthana@example.com", "phone": "9000000010", "attendance": "88%", "python": 81, "dsa": 77, "ai": 85, "overall": 81, "placement": "Eligible"},
    {"id": "STU011", "name": "Manoj K", "dept": "CSE", "year": "2nd", "email": "manoj@example.com", "phone": "9000000011", "attendance": "76%", "python": 70, "dsa": 74, "ai": 78, "overall": 74, "placement": "Not Eligible"},
    {"id": "STU012", "name": "Nandhini V", "dept": "AIDS", "year": "2nd", "email": "nandhini@example.com", "phone": "9000000012", "attendance": "94%", "python": 90, "dsa": 93, "ai": 89, "overall": 91, "placement": "Eligible"},
    {"id": "STU013", "name": "Sanjay Kumar", "dept": "IT", "year": "2nd", "email": "sanjay@example.com", "phone": "9000000013", "attendance": "83%", "python": 73, "dsa": 80, "ai": 86, "overall": 80, "placement": "Eligible"},
    {"id": "STU014", "name": "Harini S", "dept": "CSE", "year": "2nd", "email": "harini@example.com", "phone": "9000000014", "attendance": "97%", "python": 94, "dsa": 96, "ai": 95, "overall": 95, "placement": "Eligible"},
    {"id": "STU015", "name": "Ashwin R", "dept": "ECE", "year": "2nd", "email": "ashwin@example.com", "phone": "9000000015", "attendance": "79%", "python": 77, "dsa": 71, "ai": 75, "overall": 74, "placement": "Not Eligible"},
    {"id": "STU016", "name": "Meena L", "dept": "IT", "year": "2nd", "email": "meena@example.com", "phone": "9000000016", "attendance": "90%", "python": 86, "dsa": 84, "ai": 90, "overall": 87, "placement": "Eligible"},
    {"id": "STU017", "name": "Dinesh P", "dept": "EEE", "year": "2nd", "email": "dinesh@example.com", "phone": "9000000017", "attendance": "84%", "python": 69, "dsa": 76, "ai": 80, "overall": 75, "placement": "Eligible"},
    {"id": "STU018", "name": "Fathima N", "dept": "CSE", "year": "2nd", "email": "fathima@example.com", "phone": "9000000018", "attendance": "93%", "python": 89, "dsa": 91, "ai": 94, "overall": 91, "placement": "Eligible"},
    {"id": "STU019", "name": "Gokul S", "dept": "AIDS", "year": "2nd", "email": "gokul@example.com", "phone": "9000000019", "attendance": "78%", "python": 71, "dsa": 79, "ai": 73, "overall": 74, "placement": "Not Eligible"},
    {"id": "STU020", "name": "Lavanya R", "dept": "IT", "year": "2nd", "email": "lavanya@example.com", "phone": "9000000020", "attendance": "86%", "python": 83, "dsa": 87, "ai": 85, "overall": 85, "placement": "Eligible"},
    {"id": "STU021", "name": "Surya M", "dept": "CSE", "year": "2nd", "email": "surya@example.com", "phone": "9000000021", "attendance": "82%", "python": 79, "dsa": 75, "ai": 82, "overall": 79, "placement": "Eligible"},
    {"id": "STU022", "name": "Janani K", "dept": "ECE", "year": "2nd", "email": "janani@example.com", "phone": "9000000022", "attendance": "96%", "python": 92, "dsa": 90, "ai": 97, "overall": 93, "placement": "Eligible"},
    {"id": "STU023", "name": "Naveen B", "dept": "IT", "year": "2nd", "email": "naveen@example.com", "phone": "9000000023", "attendance": "72%", "python": 65, "dsa": 70, "ai": 68, "overall": 68, "placement": "Not Eligible"},
    {"id": "STU024", "name": "Reshma P", "dept": "AIDS", "year": "2nd", "email": "reshma@example.com", "phone": "9000000024", "attendance": "89%", "python": 87, "dsa": 82, "ai": 90, "overall": 86, "placement": "Eligible"},
    {"id": "STU025", "name": "Vignesh R", "dept": "CSE", "year": "2nd", "email": "vignesh@example.com", "phone": "9000000025", "attendance": "80%", "python": 76, "dsa": 78, "ai": 83, "overall": 79, "placement": "Eligible"},
]


def build_documents() -> List[Document]:
    """
    Transforms the database into rich semantic LangChain Documents.
    Creates both individual student records and departmental overview chunks.
    """
    docs: List[Document] = []

    # 1. Individual Student Semantic Documents
    for s in STUDENTS_DATA:
        content = (
            f"Student Record:\n"
            f"- Student ID: {s['id']}\n"
            f"- Full Name: {s['name']}\n"
            f"- Department: {s['dept']}\n"
            f"- Year: {s['year']}\n"
            f"- Email: {s['email']}\n"
            f"- Phone Number: {s['phone']}\n"
            f"- Attendance: {s['attendance']}\n"
            f"- Academic Marks -> Python: {s['python']}, DSA: {s['dsa']}, AI: {s['ai']}, Overall Mark: {s['overall']}\n"
            f"- Placement Status: {s['placement']}"
        )
        metadata = {
            "source": "student_database",
            "student_id": s["id"],
            "name": s["name"],
            "department": s["dept"],
            "placement": s["placement"],
        }
        docs.append(Document(page_content=content, metadata=metadata))

    # 2. Complete Summary Table Document (enables accurate aggregate lookups like highest mark, placement counts)
    table_lines = ["Complete Student Roster Table (Total 25 Students):"]
    for s in STUDENTS_DATA:
        table_lines.append(
            f"{s['id']} | {s['name']} | Dept: {s['dept']} | Attend: {s['attendance']} | "
            f"Python: {s['python']} | DSA: {s['dsa']} | AI: {s['ai']} | Overall: {s['overall']} | Placement: {s['placement']}"
        )
    full_table_content = "\n".join(table_lines)
    docs.append(Document(page_content=full_table_content, metadata={"source": "student_database_roster", "type": "aggregate_table"}))

    return docs


# ==============================================================================
# 🔍 3. RAG PIPELINE (EMBEDDINGS, VECTOR STORE & LCEL CHAIN)
# ==============================================================================

class StudentRAGSystem:
    """Encapsulates the complete LangChain RAG pipeline for the student database."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        print("🔧 Initializing Google Generative AI Embeddings...")
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            api_key=self.api_key,
        )

        print("📦 Building and indexing Vector Store in memory...")
        self.vector_store = InMemoryVectorStore(self.embeddings)
        docs = build_documents()
        self.vector_store.add_documents(docs)
        print(f"✅ Indexed {len(docs)} documents into InMemoryVectorStore!")

        # Retriever
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

        # LLM
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            api_key=self.api_key,
            temperature=0.0,
            max_retries=5,
        )

        # RAG Prompt Template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an accurate, helpful Document QA assistant specialized in the Dummy Student Database.\n"
                "Use the following retrieved context documents to answer the user's question accurately.\n"
                "RULES:\n"
                "1. Base your answer strictly on the provided context.\n"
                "2. When mentioning students, include relevant details like Student ID, Department, Marks, or Contact if helpful.\n"
                "3. If performing an aggregation (e.g. counting, finding highest/lowest), double-check all matching records in the context.\n"
                "4. Be concise, direct, and structured in your response.\n\n"
                "Retrieved Context:\n{context}"
            )),
            ("human", "{question}")
        ])

        # LCEL Chain
        def format_docs(retrieved_docs: List[Document]) -> str:
            return "\n\n---\n\n".join(d.page_content for d in retrieved_docs)

        self.chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, question: str) -> str:
        """Retrieves context and generates an answer for the given question."""
        return self.chain.invoke(question)


# ==============================================================================
# 🎯 4. SUGGESTED QUESTIONS BENCHMARK (FROM THE DOCUMENT PAGE 2)
# ==============================================================================
SUGGESTED_QUESTIONS = [
    "What is Priya Sharma's attendance and overall mark?",
    "Who has the highest overall mark?",
    "Which students belong to the CSE department?",
    "List students whose attendance is below 75%.",
    "Who scored above 90 in AI?",
    "How many students are placement eligible?",
    "What is Arjun Kumar's DSA mark?",
    "Which student has the highest attendance?",
    "Find all AIDS students with an overall mark above 80.",
    "What is the phone number of Fathima N?",
]


def run_suggested_questions(rag_system: StudentRAGSystem):
    """Executes all 10 suggested questions from the uploaded PDF document."""
    print("\n" + "=" * 80)
    print("📋 RUNNING 10 SUGGESTED RAG QUESTIONS FROM THE DOCUMENT")
    print("=" * 80)

    for i, q in enumerate(SUGGESTED_QUESTIONS, 1):
        print(f"\n❓ [Q{i}]: {q}")
        t0 = time.time()
        answer = rag_system.ask(q)
        dt = time.time() - t0
        print(f"💡 [Answer in {dt:.2f}s]:\n{answer.strip()}")
        print("-" * 80)


# ==============================================================================
# 🚀 5. MAIN ENTRY POINT & INTERACTIVE CHAT
# ==============================================================================
def main():
    print("=" * 80)
    print("   STUDENT DATABASE RAG SYSTEM (LANGCHAIN + GEMINI EMBEDDINGS)   ")
    print("=" * 80)

    api_key = get_active_api_key()
    rag = StudentRAGSystem(api_key=api_key)

    # 1. Run the 10 questions from the PDF
    run_suggested_questions(rag)

    # 2. Interactive QA
    print("\n" + "=" * 80)
    print("💬 INTERACTIVE RAG MODE: Ask any custom question about the Student Database!")
    print("Examples:")
    print("  • 'What is the email of Divya S?'")
    print("  • 'Which ECE students scored more than 80 in Python?'")
    print("  • 'List all students who are Not Eligible for placement'")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_q = input("Question > ").strip()
            if not user_q:
                continue
            if user_q.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break

            ans = rag.ask(user_q)
            print(f"\n💡 Answer:\n{ans}\n")
            print("-" * 80)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        except Exception as e:
            print(f"\n[Error]: {e}\n")


if __name__ == "__main__":
    main()
