# text_to_sql.py
import os
from langchain_groq import ChatGroq
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from db_connector import get_connection

load_dotenv()

use_bedrock = os.getenv("USE_BEDROCK", "false").lower() == "true"

def get_schema() -> str:
    """PostgreSQL database ka schema fetch karta hai"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all tables in public schema
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    
    schema = ""
    for table in tables:
        table_name = table[0]
        # Get column info
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
        """)
        columns = cursor.fetchall()
        col_info = ", ".join([f"{col[0]} ({col[1]})" for col in columns])
        schema += f"Table: {table_name} | Columns: {col_info}\n"
    
    cursor.close()
    conn.close()
    return schema

def answer_with_sql(question: str) -> str:
    """Natural language question ko SQL query mein convert karke answer deta hai"""
    
    # Choose LLM
    if use_bedrock:
        llm = ChatBedrock(
            model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            region_name="us-east-1",
            model_kwargs={"temperature": 0, "max_tokens": 1000}
        )
    else:
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",
            temperature=0
        )
    
    schema = get_schema()
    
    # Prompt template
    template = """You are a SQL expert. Given a database schema and a question, generate a valid PostgreSQL query.

Database Schema:
{schema}

Question: {question}

Return ONLY the SQL query, nothing else. Use PostgreSQL syntax."""

    prompt = PromptTemplate(template=template, input_variables=["schema", "question"])
    chain = prompt | llm
    
    # Generate SQL
    sql_query = chain.invoke({"schema": schema, "question": question}).content.strip()
    
    # Remove markdown code blocks if present
    if sql_query.startswith("```"):
        sql_query = sql_query.split("\n", 1)[1]
        sql_query = sql_query.rsplit("```", 1)[0].strip()
    
    print(f"🔢 Generated SQL: {sql_query}")
    
    # Execute SQL  ← ADD FROM HERE
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not results:
            return "No results found."
        
        # Format results nicely
        if len(results) == 1 and len(results[0]) == 1:
            # Single value (e.g., count, max)
            return str(results[0][0])
        else:
            # Multiple rows/columns - format as list
            formatted = []
            for row in results:
                if len(row) == 1:
                    formatted.append(str(row[0]))
                else:
                    formatted.append(" | ".join(str(val) for val in row))
            return "\n".join(formatted)
        
    except Exception as e:
        return f"SQL Error: {str(e)}"
    
