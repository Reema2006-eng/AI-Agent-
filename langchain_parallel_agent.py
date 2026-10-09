"""
================================================================================
⚡ LANGCHAIN PARALLEL MULTI-TASK AGENT (4 Tools Integrated)
================================================================================
This script demonstrates how to execute MULTIPLE AGENT TASKS AT THE SAME TIME
using LangChain and Google Gemini across 4 integrated tools:
  1. `basic_calculator`: Arithmetic computations
  2. `web_search`: Live Web Search (DuckDuckGo + Wikipedia)
  3. `get_current_datetime`: Current date, time, year & day of week
  4. `document_search`: Retrieves student records from the Student Database

Concurrency Engine: Asyncio + LangChain ainvoke / abatch
================================================================================
"""

import os
import sys
import time
import json
import re
import urllib.request
import urllib.parse
import datetime
import asyncio
from typing import List, Dict, Any

# Ensure UTF-8 output in Windows PowerShell/Command Prompt
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# LangChain and LangGraph imports
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI


# ==============================================================================
# 🔑 1. YOUR GEMINI API KEY & MODEL CONFIGURATION
# ==============================================================================
GEMINI_API_KEY = ""

# gemini-3.1-flash-lite is chosen for high rate-limits & fast throughput
DEFAULT_MODEL = "gemini-3.1-flash-lite"


def get_active_api_key() -> str:
    """Retrieves the API key from variable, environment, or console input."""
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
# 📄 2. STUDENT DATABASE DOCUMENT STORE
# ==============================================================================
STUDENT_RECORDS = [
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


# ==============================================================================
# 📋 3. LANGCHAIN TOOL DEFINITIONS (@tool Decorator)
# ==============================================================================

@tool
def basic_calculator(operation: str, a: float, b: float) -> str:
    """Performs arithmetic calculations between two numbers.
    Operations supported: 'add', 'subtract', 'multiply', 'divide'.
    """
    op = str(operation).lower().strip()
    try:
        a_val, b_val = float(a), float(b)
    except Exception as e:
        return f"Error: Invalid numbers ({e})"

    if op == "add":
        res = a_val + b_val
    elif op == "subtract":
        res = a_val - b_val
    elif op == "multiply":
        res = a_val * b_val
    elif op == "divide":
        if b_val == 0:
            return "Error: Division by zero is undefined."
        res = a_val / b_val
    else:
        return f"Error: Unsupported operation '{operation}'."

    if isinstance(res, float) and res.is_integer():
        return str(int(res))
    return str(round(res, 6))


@tool
def web_search(query: str) -> str:
    """Searches the web for up-to-date facts, information, and definitions.
    Returns concise summaries and top source links.
    """
    clean_q = str(query).strip()
    if not clean_q:
        return "Error: Empty search query."

    try:
        ddg_url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode({
            "q": clean_q, "format": "json", "no_html": "1"
        })
        req = urllib.request.Request(ddg_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            if data.get("AbstractText"):
                return f"Source ({data.get('Heading')}): {data.get('AbstractText')}"
    except Exception:
        pass

    try:
        wiki_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "list": "search", "srsearch": clean_q, "format": "json", "utf8": "1", "srlimit": "2"
        })
        req = urllib.request.Request(wiki_url, headers={"User-Agent": "LangChainParallelAgent/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            items = data.get("query", {}).get("search", [])
            if items:
                snippets = [f"{item['title']}: {re.sub(r'<[^>]+>', '', item['snippet'])}" for item in items]
                return "\n".join(snippets)
    except Exception as e:
        return f"Search error: {e}"

    return "No direct search results found."


@tool
def get_current_datetime(timezone: str = "local") -> str:
    """Retrieves current date, time, year, month, day, and day of the week.
    Timezone can be 'local' or 'UTC'.
    """
    tz = str(timezone).lower().strip() if timezone else "local"
    if tz == "utc":
        now = datetime.datetime.now(datetime.timezone.utc)
        label = "UTC"
    else:
        now = datetime.datetime.now()
        label = "Local System Time"

    return (
        f"Date: {now.strftime('%Y-%m-%d')}, "
        f"Time: {now.strftime('%H:%M:%S')}, "
        f"Day: {now.strftime('%A')}, "
        f"Year: {now.year} ({label})"
    )


@tool
def document_search(query: str) -> str:
    """Searches the official Dummy Student Database document for student records,
    marks (Python, DSA, AI, Overall), attendance percentage, department, phone, email, and placement.
    """
    q = str(query).lower().strip()
    if not q:
        return "Error: Empty document search query."

    matches = []
    for s in STUDENT_RECORDS:
        name_tokens = s["name"].lower().split()
        if any(token in q for token in name_tokens if len(token) > 2) or s["id"].lower() in q:
            matches.append(s)

    if not matches:
        for s in STUDENT_RECORDS:
            if re.search(r"\b" + re.escape(s["dept"].lower()) + r"\b", q):
                matches.append(s)

    aggregate_keywords = ["highest", "lowest", "below", "above", "eligible", "all", "how many", "compare", "best", "rank"]
    if not matches or any(kw in q for kw in aggregate_keywords):
        return json.dumps(STUDENT_RECORDS, indent=2)

    return json.dumps(matches, indent=2)


# ==============================================================================
# 🤖 4. AGENT FACTORY
# ==============================================================================

def create_langchain_agent(api_key: str, model_name: str = DEFAULT_MODEL):
    """Initializes the LangChain Agent with all 4 tools."""
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        api_key=api_key,
        temperature=0.0,
        max_retries=5,
    )
    tools = [document_search, basic_calculator, web_search, get_current_datetime]

    system_prompt = (
        "You are an expert AI agent equipped with 4 tools: document_search, basic_calculator, web_search, and get_current_datetime.\n"
        "Always use document_search for questions about the Student Database document.\n"
        "Always use basic_calculator for any arithmetic. Provide clear, accurate answers."
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )
    return agent


def extract_response_text(agent_output: Dict[str, Any]) -> str:
    """Extracts human-readable response text from LangChain agent state."""
    messages = agent_output.get("messages", [])
    if not messages:
        return "No response generated."
    last_msg = messages[-1].content
    if isinstance(last_msg, list):
        return "".join([part.get("text", "") for part in last_msg if isinstance(part, dict)]).strip()
    return str(last_msg).strip()


# ==============================================================================
# ⚡ 5. PARALLEL MULTI-TASK EXECUTION (asyncio.gather)
# ==============================================================================

async def execute_tasks_in_parallel(agent, task_list: List[str]):
    """Executes multiple user queries concurrently at the exact same time."""
    print("\n" + "=" * 75)
    print(f"🚀 LAUNCHING {len(task_list)} TASKS CONCURRENTLY AT THE SAME TIME")
    print("=" * 75)

    start_all = time.time()

    async def worker(task_id: int, query: str):
        t_start = time.time()
        print(f"   ⏳ [Task #{task_id} STARTED] at +{time.time() - start_all:.2f}s: \"{query}\"")

        result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
        answer = extract_response_text(result)

        elapsed = time.time() - t_start
        print(f"\n   ✅ [Task #{task_id} FINISHED in {elapsed:.2f}s]:")
        print(f"      Query:  \"{query}\"")
        print(f"      Answer: {answer}\n")
        return {"id": task_id, "query": query, "answer": answer, "time": elapsed}

    results = await asyncio.gather(*[worker(i + 1, q) for i, q in enumerate(task_list)])

    total_time = time.time() - start_all
    sum_individual = sum(r["time"] for r in results)

    print("=" * 75)
    print("📊 PARALLEL EXECUTION SUMMARY:")
    print("=" * 75)
    print(f"• Total Tasks:                 {len(task_list)}")
    print(f"• Wall-Clock Parallel Time:    {total_time:.2f} seconds")
    print(f"• Sequential Equivalent Time:  {sum_individual:.2f} seconds")
    if sum_individual > 0:
        speedup = (sum_individual / total_time)
        print(f"• Speedup Factor:              {speedup:.2f}x faster than running sequentially!")
    print("=" * 75 + "\n")


# ==============================================================================
# 🚀 6. MAIN DEMO & INTERACTIVE CLI
# ==============================================================================

async def main_async():
    print("=" * 75)
    print("   LANGCHAIN PARALLEL MULTI-TASK AGENT (4 TOOLS INTEGRATED)   ")
    print("=" * 75)
    print("• Tool 1: document_search     (Student Database Document)")
    print("• Tool 2: basic_calculator    (Arithmetic operations)")
    print("• Tool 3: web_search          (Live DuckDuckGo & Wikipedia search)")
    print("• Tool 4: get_current_datetime (System Date & Time)")
    print("• Parallel Engine: Asyncio + LangChain ainvoke")
    print("=" * 75)

    api_key = get_active_api_key()
    agent = create_langchain_agent(api_key=api_key, model_name=DEFAULT_MODEL)

    print(f"\n✅ LangChain Agent initialized with 4 tools! Model: '{DEFAULT_MODEL}'")

    demo_tasks = [
        "What is Priya Sharma attendance and overall mark in the document?",
        "What is 25 multiplied by 4, then add 50?",
        "What is today date and day of the week?",
    ]

    print("\nRunning demonstration with 3 concurrent tasks:")
    for i, t in enumerate(demo_tasks, 1):
        print(f"  Task {i}: {t}")

    await execute_tasks_in_parallel(agent, demo_tasks)

    print("---------------------------------------------------------------------------")
    print("💡 INTERACTIVE MULTI-TASK MODE")
    print("Enter multiple tasks separated by semicolons (;) to run them simultaneously!")
    print("Example: 'What is Arjun Kumar DSA mark? ; What is 500 / 4 ; What time is it now?'")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            raw_input = input("Enter tasks (separated by ';') > ").strip()
            if not raw_input:
                continue
            if raw_input.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break

            tasks = [t.strip() for t in raw_input.split(";") if t.strip()]
            if not tasks:
                continue

            await execute_tasks_in_parallel(agent, tasks)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        except Exception as e:
            print(f"\n[Error]: {e}\n")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
