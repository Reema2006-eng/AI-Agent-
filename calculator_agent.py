"""
================================================================================
🧮 REACT PATTERN AGENT: 4 INTEGRATED TOOLS (Zero Framework)
================================================================================
This script implements the classic ReAct (Reasoning + Acting) Agent pattern
equipped with FOUR distinct tools:
  1. `basic_calculator`: Arithmetic computations (JSON Schema Tool)
  2. `web_search`: Live Web Search via DuckDuckGo & Wikipedia (JSON Schema Tool)
  3. `get_current_datetime`: Current date, time, year & day of week (JSON Schema Tool)
  4. `document_search`: Retrieves student records, marks, attendance, and details
     from the official Student Database document (JSON Schema Tool)

Frameworks: ZERO (Standard library + official `google-genai` SDK only).
================================================================================
"""

import os
import sys
import json
import time
import re
import datetime
import urllib.request
import urllib.parse
from typing import Dict, Any, List

# Ensure clean UTF-8 text printing on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from google import genai
from google.genai import types


# ==============================================================================
# 🔑 1. YOUR GEMINI API KEY & MODEL SELECTION
# ==============================================================================
# Paste your Gemini AI Studio API key between the quotes below:
GEMINI_API_KEY = ""

# Model Priority with Automatic Fallback.
# If a model reaches free-tier RPM/RPD limits (429), it switches automatically.
MODEL_FALLBACK_LIST = [
    "gemini-3.5-flash",        # Primary: fast, accurate ReAct reasoning
    "gemini-3.1-flash-lite",   # Fallback 1: very high rate limits
    "gemini-3.7-flash",        # Fallback 2: advanced multi-step reasoning
    "gemini-3.5-flash-lite",   # Fallback 3: backup lightweight model
    "gemini-3.8-flash",        # Fallback 4: available when reset finishes
]


def get_active_api_key() -> str:
    """Retrieves the API key from the script variable, environment, or user prompt."""
    global GEMINI_API_KEY
    if GEMINI_API_KEY and GEMINI_API_KEY.strip() and GEMINI_API_KEY.strip() != "YOUR_GEMINI_API_KEY_HERE":
        return GEMINI_API_KEY.strip()

    # Check environment variables
    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # Fallback to interactive console input
    print("\n[!] No API key found in the GEMINI_API_KEY variable or environment.")
    entered_key = input("Please paste your Gemini AI Studio API Key: ").strip()
    if not entered_key:
        print("[Error] An API key is required to run the agent. Exiting.")
        sys.exit(1)
    return entered_key


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
# 📋 3. TOOL DEFINITIONS (JSON SCHEMA FORMAT)
# ==============================================================================

# Tool 1: Calculator Tool Schema
CALCULATOR_TOOL_SCHEMA: Dict[str, Any] = {
    "name": "basic_calculator",
    "description": (
        "Performs basic arithmetic operations between two numbers. "
        "Supports operations: 'add', 'subtract', 'multiply', and 'divide'."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "operation": {
                "type": "STRING",
                "description": "The mathematical operation to perform.",
                "enum": ["add", "subtract", "multiply", "divide"],
            },
            "a": {
                "type": "NUMBER",
                "description": "The first number (operand 1, minuend, or dividend).",
            },
            "b": {
                "type": "NUMBER",
                "description": "The second number (operand 2, subtrahend, or divisor).",
            },
        },
        "required": ["operation", "a", "b"],
    },
}

# Tool 2: Web Search Tool Schema
WEB_SEARCH_TOOL_SCHEMA: Dict[str, Any] = {
    "name": "web_search",
    "description": (
        "Searches the web for up-to-date facts, information, definitions, and real-world data. "
        "Returns search result titles, snippets/summaries, and source links."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search keywords or query to look up on the web.",
            },
        },
        "required": ["query"],
    },
}

# Tool 3: Date & Time Tool Schema
DATETIME_TOOL_SCHEMA: Dict[str, Any] = {
    "name": "get_current_datetime",
    "description": (
        "Retrieves the current date, time, year, month, day, and day of the week. "
        "Use this tool whenever you need today's date, current time, day of the week, "
        "or need to calculate ages or durations."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "timezone": {
                "type": "STRING",
                "description": "Optional timezone: 'local' (default) or 'UTC'.",
            },
        },
    },
}

# Tool 4: Document Search Tool Schema (RAG Tool)
DOCUMENT_SEARCH_TOOL_SCHEMA: Dict[str, Any] = {
    "name": "document_search",
    "description": (
        "Searches the official Dummy Student Database document. "
        "Retrieves academic records, marks (Python, DSA, AI, Overall), attendance percentage, "
        "department (CSE, IT, ECE, AIDS, EEE), email, phone number, and placement eligibility for 25 students."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query (e.g. 'Priya Sharma', 'STU014', 'CSE students', 'highest overall mark', 'attendance below 75%').",
            },
        },
        "required": ["query"],
    },
}


# ==============================================================================
# ⚙️ 4. LOCAL PYTHON TOOL IMPLEMENTATIONS
# ==============================================================================

def execute_calculator(operation: str, a: float, b: float) -> Dict[str, Any]:
    """Executes arithmetic calculation using parameters emitted by LLM."""
    try:
        a_val = float(a)
        b_val = float(b)
    except (ValueError, TypeError) as e:
        return {"error": f"Invalid numerical inputs: a={a}, b={b}. Error: {str(e)}"}

    op = str(operation).lower().strip()

    if op == "add":
        result = a_val + b_val
    elif op == "subtract":
        result = a_val - b_val
    elif op == "multiply":
        result = a_val * b_val
    elif op == "divide":
        if b_val == 0:
            return {"error": "Division by zero is undefined."}
        result = a_val / b_val
    else:
        return {"error": f"Unsupported operation '{operation}'. Must be: add, subtract, multiply, or divide."}

    if isinstance(result, float) and result.is_integer():
        result = int(result)
    else:
        result = round(result, 6)

    return {
        "operation": op,
        "a": a_val,
        "b": b_val,
        "result": result,
    }


def execute_web_search(query: str) -> Dict[str, Any]:
    """Executes web search using DuckDuckGo with Wikipedia fallback (urllib only)."""
    clean_query = str(query).strip()
    if not clean_query:
        return {"error": "Search query cannot be empty."}

    results: List[Dict[str, str]] = []

    # 1. DuckDuckGo Instant Answer API
    try:
        ddg_url = "https://api.duckduckgo.com/?" + urllib.parse.urlencode({
            "q": clean_query,
            "format": "json",
            "no_html": "1"
        })
        ddg_req = urllib.request.Request(ddg_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(ddg_req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            if data.get("AbstractText"):
                results.append({
                    "title": data.get("Heading") or clean_query,
                    "snippet": data.get("AbstractText"),
                    "url": data.get("AbstractURL", "")
                })
            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:60],
                        "snippet": topic.get("Text", ""),
                        "url": topic.get("FirstURL", "")
                    })
    except Exception:
        pass

    # 2. Wikipedia API fallback
    if not results:
        try:
            wiki_url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
                "action": "query",
                "list": "search",
                "srsearch": clean_query,
                "format": "json",
                "utf8": "1",
                "srlimit": "3"
            })
            wiki_req = urllib.request.Request(wiki_url, headers={"User-Agent": "AgenticAiApp/1.0 (calculator-agent)"})
            with urllib.request.urlopen(wiki_req, timeout=8) as resp:
                wiki_data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                for item in wiki_data.get("query", {}).get("search", []):
                    clean_snippet = re.sub(r"<[^>]+>", "", item.get("snippet", "")).strip()
                    title = item.get("title", "")
                    url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}"
                    results.append({
                        "title": title,
                        "snippet": clean_snippet,
                        "url": url
                    })
        except Exception as e:
            return {"query": clean_query, "error": f"Search failed: {e}", "results": []}

    if not results:
        return {"query": clean_query, "message": "No relevant search results found.", "results": []}

    return {"query": clean_query, "results": results[:3]}


def execute_datetime_tool(timezone: str = "local") -> Dict[str, Any]:
    """Retrieves current date and time using standard datetime module."""
    tz_choice = str(timezone).lower().strip() if timezone else "local"

    if tz_choice == "utc":
        now = datetime.datetime.now(datetime.timezone.utc)
        tz_label = "UTC"
    else:
        now = datetime.datetime.now()
        tz_label = "Local System Time"

    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "iso_timestamp": now.isoformat(),
        "timezone": tz_label,
    }


def execute_document_search(query: str) -> Dict[str, Any]:
    """
    Searches the official Student Database document.
    Performs precise record extraction for individual students and departments,
    and returns complete roster tables for aggregate queries.
    """
    q = str(query).lower().strip()
    if not q:
        return {"error": "Document search query cannot be empty."}

    matched_records: List[Dict[str, Any]] = []

    # 1. Search by student name tokens or student ID
    for s in STUDENT_RECORDS:
        name_parts = s["name"].lower().split()
        if any(part in q for part in name_parts if len(part) > 2) or s["id"].lower() in q:
            matched_records.append(s)

    # 2. Search by department if no single student matched
    if not matched_records:
        for s in STUDENT_RECORDS:
            if re.search(r"\b" + re.escape(s["dept"].lower()) + r"\b", q):
                matched_records.append(s)

    # 3. For aggregate queries (highest, lowest, attendance below/above, count, all)
    aggregate_keywords = ["highest", "lowest", "below", "above", "eligible", "all", "how many", "compare", "best", "rank"]
    if not matched_records or any(kw in q for kw in aggregate_keywords):
        return {
            "query": query,
            "type": "database_roster",
            "total_records": len(STUDENT_RECORDS),
            "records": STUDENT_RECORDS,
        }

    return {
        "query": query,
        "type": "specific_records",
        "matches_found": len(matched_records),
        "records": matched_records,
    }


# ==============================================================================
# 🤖 5. REACT (REASON + ACTION) AGENT ENGINE
# ==============================================================================
class ReActAgent:
    """
    Implements the ReAct (Reasoning + Acting) Agent Pattern.
    Equipped with 4 tools:
      • basic_calculator
      • web_search
      • get_current_datetime
      • document_search
    """

    def __init__(self, api_key: str, model_list: List[str] = MODEL_FALLBACK_LIST):
        self.api_key = api_key
        self.model_list = model_list
        self.current_model_idx = 0
        self.client = genai.Client(api_key=self.api_key)

        # Register all 4 tools
        self.tools = [
            types.Tool(
                function_declarations=[
                    CALCULATOR_TOOL_SCHEMA,
                    WEB_SEARCH_TOOL_SCHEMA,
                    DATETIME_TOOL_SCHEMA,
                    DOCUMENT_SEARCH_TOOL_SCHEMA,
                ]
            )
        ]

        # ReAct System Instruction
        self.system_instruction = (
            "You are an autonomous AI Agent that strictly follows the ReAct (Reasoning + Acting) pattern.\n\n"
            "OPERATING INSTRUCTIONS:\n"
            "For every action you take, you MUST explicitly formulate a 'Thought' explaining:\n"
            "  - What you know so far.\n"
            "  - What step you are taking next.\n"
            "  - Why you are invoking this specific tool.\n\n"
            "Always include your text reasoning (Thought) alongside your tool call (Action).\n"
            "When you receive the tool output (Observation), reflect on it in your next Thought.\n"
            "When you have all the necessary information, formulate your final thought and provide the Final Answer.\n\n"
            "TOOLS AT YOUR DISPOSAL:\n"
            "1. 'document_search': Use for ANY questions about the Student Database (marks, attendance, departments, phone, email, placement).\n"
            "2. 'basic_calculator': Use for ALL math calculations (add, subtract, multiply, divide). NEVER approximate math.\n"
            "3. 'web_search': Use for external facts, global information, or current events.\n"
            "4. 'get_current_datetime': Use for today's date, current time, day of the week, or year.\n\n"
            "CHAINING EXAMPLES:\n"
            "- If a user asks 'What is Arjun Kumar's DSA mark and multiply it by 2?', "
            "  first call 'document_search' to find the mark, then call 'basic_calculator' to multiply by 2!"
        )

    @property
    def current_model(self) -> str:
        return self.model_list[self.current_model_idx]

    def _call_gemini_with_fallback(
        self, contents: List[types.Content], config: types.GenerateContentConfig
    ) -> Any:
        """Calls Gemini with automatic fallback across models on 429/503 errors."""
        while self.current_model_idx < len(self.model_list):
            model_to_try = self.current_model
            try:
                response = self.client.models.generate_content(
                    model=model_to_try,
                    contents=contents,
                    config=config,
                )
                return response
            except Exception as e:
                err_text = str(e)
                is_quota_exhausted = "429" in err_text or "RESOURCE_EXHAUSTED" in err_text
                is_server_busy = "503" in err_text or "UNAVAILABLE" in err_text

                if is_quota_exhausted or is_server_busy:
                    reason = "Quota limit (429)" if is_quota_exhausted else "Server busy (503)"
                    print(f"\n⚠️  [Model Notice] '{model_to_try}' reached {reason}.")

                    self.current_model_idx += 1
                    if self.current_model_idx < len(self.model_list):
                        next_model = self.model_list[self.current_model_idx]
                        print(f"👉 Switching to fallback model: '{next_model}'...\n")
                        continue
                    else:
                        print("❌ All fallback models exhausted.")
                        raise e
                else:
                    raise e

    def run(self, user_prompt: str, max_iterations: int = 6) -> str:
        """Executes the ReAct Loop with all 4 tools."""
        print("\n" + "=" * 75)
        print(f"👤 USER QUERY: {user_prompt}")
        print("=" * 75)

        history: List[types.Content] = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_prompt)]
            )
        ]

        config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            tools=self.tools,
            temperature=0.0,
        )

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 [Iteration {iteration}] Calling Model ({self.current_model})...")

            try:
                response = self._call_gemini_with_fallback(contents=history, config=config)
            except Exception as e:
                print(f"❌ [API Error]: {e}")
                return f"Error: {e}"

            if not response.candidates or not response.candidates[0].content:
                return "Error: Empty response received from model."

            model_content = response.candidates[0].content
            parts = model_content.parts or []

            history.append(model_content)

            thought_text = "".join([p.text for p in parts if p.text]).strip()
            function_calls = [p.function_call for p in parts if p.function_call is not None]

            if function_calls:
                print("\n" + "─" * 65)
                if thought_text:
                    print(f"🧠 THOUGHT (Reason):")
                    cleaned_thought = re.sub(r"^(Thought:\s*)", "", thought_text, flags=re.IGNORECASE)
                    print(f"   {cleaned_thought}")
                else:
                    call_preview = function_calls[0]
                    print(f"🧠 THOUGHT (Reason):")
                    print(f"   Decided to invoke `{call_preview.name}` with parameters: {dict(call_preview.args)}")

                tool_response_parts: List[types.Part] = []

                for call in function_calls:
                    tool_name = call.name
                    tool_args = dict(call.args) if call.args else {}

                    print(f"\n⚡ ACTION (Act):")
                    print(f"   Tool Name: {tool_name}")
                    print(f"   Input JSON from LLM: {json.dumps(tool_args, indent=2)}")

                    # Dispatch to corresponding tool
                    if tool_name == "basic_calculator":
                        op = tool_args.get("operation", "")
                        a = tool_args.get("a", 0)
                        b = tool_args.get("b", 0)
                        result = execute_calculator(operation=op, a=a, b=b)

                    elif tool_name == "web_search":
                        query = tool_args.get("query", "")
                        result = execute_web_search(query=query)

                    elif tool_name == "get_current_datetime":
                        tz = tool_args.get("timezone", "local")
                        result = execute_datetime_tool(timezone=tz)

                    elif tool_name == "document_search":
                        query = tool_args.get("query", "")
                        result = execute_document_search(query=query)

                    else:
                        result = {"error": f"Unknown tool '{tool_name}'."}

                    print(f"\n👁️  OBSERVATION (Tool Output):")
                    # If returning full roster, print preview to keep console clean
                    if result.get("type") == "database_roster":
                        print(f"   Output JSON to LLM: [Retrieved complete 25-student database roster]")
                    else:
                        print(f"   Output JSON to LLM: {json.dumps(result, indent=2)}")
                    print("─" * 65)

                    part = types.Part.from_function_response(
                        name=tool_name,
                        response=result
                    )
                    tool_response_parts.append(part)

                history.append(types.Content(role="user", parts=tool_response_parts))
                continue

            else:
                print("\n" + "=" * 75)
                print("🏁 FINAL ANSWER:")
                print("=" * 75)
                final_answer = re.sub(r"^(Final Answer:\s*)", "", thought_text, flags=re.IGNORECASE)
                print(final_answer.strip())
                print("=" * 75 + "\n")
                return final_answer.strip()

        return "Agent stopped: Reached maximum iterations."


# ==============================================================================
# 🚀 6. MAIN INTERACTIVE EXECUTION
# ==============================================================================
def main():
    print("=" * 75)
    print("      REACT MULTI-TOOL AGENT (4 TOOLS INTEGRATED)      ")
    print("=" * 75)
    print("• Tool 1: 'document_search'     (Dummy Student Database Document RAG)")
    print("• Tool 2: 'basic_calculator'    (Arithmetic calculations in JSON format)")
    print("• Tool 3: 'web_search'          (Live Web Search via DuckDuckGo & Wikipedia)")
    print("• Tool 4: 'get_current_datetime' (Live System Date & Time)")
    print("• Frameworks: Zero (Standard Library + google-genai)")
    print("=" * 75)

    api_key = get_active_api_key()
    agent = ReActAgent(api_key=api_key)

    print(f"\n✅ ReAct Agent initialized with 4 tools! Primary model: '{agent.current_model}'")
    print("\nTry testing:")
    print("  1. Document QA:   'What is Priya Sharma attendance and overall mark?'")
    print("  2. Chained QA:    'What is Arjun Kumar DSA mark and multiply it by 3?'")
    print("  3. Aggregate QA:  'Who has the highest overall mark in the document?'")
    print("  4. Date + Search: 'What day is it today and search the capital of Japan'")
    print("Type 'exit' or 'quit' to quit.\n")

    while True:
        try:
            user_input = input("You > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break

            agent.run(user_input)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
        except Exception as err:
            print(f"\n[Error]: {err}\n")


if __name__ == "__main__":
    main()
