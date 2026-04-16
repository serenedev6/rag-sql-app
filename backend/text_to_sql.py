# text_to_sql.py
import sqlite3
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

SQLITE_PATH = os.getenv("SQLITE_PATH", "sample.db")


def get_schema() -> str:
    """SQLite database ka schema fetch karta hai"""
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    schema = ""
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        col_names = ", ".join([col[1] for col in columns])
        schema += f"Table: {table_name} | Columns: {col_names}\n"

    conn.close()
    return schema


def run_sql_query(query: str) -> list:
    """SQL query run karta hai aur results deta hai"""
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def answer_with_sql(question: str) -> str:
    """
    Natural language sawaal ko SQL mein convert karta hai
    aur answer deta hai.
    """
    schema = get_schema()

    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    # Step 1: SQL query generate karo
    sql_prompt = PromptTemplate.from_template("""
Tum ek SQL expert ho. Neeche diye gaye database schema ke basis par 
sawaal ka jawab dene ke liye sirf SQL query likho.

Schema:
{schema}

Sawaal: {question}

Rules:
- Sirf SQL query likho — koi explanation nahi
- Query SQLite compatible honi chahiye
- Query sirf ek line mein likho
- Koi markdown ya backticks mat use karo

SQL Query:
""")

    sql_chain = sql_prompt | llm
    sql_response = sql_chain.invoke({
        "schema": schema,
        "question": question
    })

    sql_query = sql_response.content.strip()
    print(f"🔧 Generated SQL: {sql_query}")

    # Step 2: Query run karo
    try:
        results = run_sql_query(sql_query)
    except Exception as e:
        return f"SQL Error: {e}"

    # Step 3: Results ko natural language mein convert karo
    answer_prompt = PromptTemplate.from_template("""
Sawaal: {question}
SQL Query: {sql_query}
Results: {results}

In results ke basis par sawaal ka simple aur clear jawab do Hindi mein.
Sirf jawab do — koi extra explanation nahi.

Jawab:
""")

    answer_chain = answer_prompt | llm
    answer = answer_chain.invoke({
        "question": question,
        "sql_query": sql_query,
        "results": str(results)
    })

    return answer.content.strip()