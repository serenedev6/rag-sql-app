from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

use_bedrock = os.getenv("USE_BEDROCK", "false").lower() == "true"

# Define tools
@tool
def sql_query_tool(question: str) -> str:
    """Execute SQL queries for structured data questions like counts, max, min, filtering.
    Use for: 'most expensive', 'how many', 'list all', 'cheapest', etc."""
    from text_to_sql import answer_with_sql
    return answer_with_sql(question)

@tool
def rag_search_tool(question: str) -> str:
    """Search product/customer/order descriptions using semantic search.
    Use for: 'tell me about', 'describe', 'what is', 'similar to', etc."""
    from rag_chain import ask_question as rag_ask, create_rag_chain
    from chat.views import VECTOR_STORE, RAG_CHAIN
    
    global RAG_CHAIN
    if RAG_CHAIN is None:
        RAG_CHAIN = create_rag_chain(VECTOR_STORE, top_k=10)
    
    result = rag_ask(RAG_CHAIN, question)
    return result["answer"]

def ask_agent(question: str) -> str:
    """Simple agent that decides which tool to use and executes it"""
    
    # Choose LLM
    if use_bedrock:
        llm = ChatBedrock(
            model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            region_name="us-east-1",
            model_kwargs={"temperature": 0, "max_tokens": 2000}
        )
    else:
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",
            temperature=0
        )
    
    # Step 1: Decide which tool(s) to use
    decision_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a routing assistant. Analyze the user's question and decide which tool(s) to use:

- sql_query: For questions needing exact data (counts, max/min, filtering, "how many", "most expensive", "list all")
- rag_search: For questions needing descriptions ("tell me about", "describe", "what is")
- both: For complex questions needing both data AND descriptions

Respond with ONLY: "sql_query", "rag_search", or "both" """),
        ("human", "{question}")
    ])
    
    decision_chain = decision_prompt | llm | StrOutputParser()
    tool_choice = decision_chain.invoke({"question": question}).strip().lower()
    
    print(f"🤖 Agent decision: {tool_choice}")
    
    # Step 2: Execute tool(s)
    if "both" in tool_choice:
        # Use both tools
        print("🔧 Using SQL tool...")
        sql_result = sql_query_tool.invoke(question)
        print("🔧 Using RAG tool...")
        rag_result = rag_search_tool.invoke(question)
        
        # Step 3: Combine results
        combine_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Combine the SQL data and descriptions into a clear answer."),
            ("human", """Question: {question}

SQL Data: {sql_data}

Descriptions: {rag_data}

Provide a complete answer combining both sources.""")
        ])
        
        combine_chain = combine_prompt | llm | StrOutputParser()
        answer = combine_chain.invoke({
            "question": question,
            "sql_data": sql_result,
            "rag_data": rag_result
        })
        
    elif "sql" in tool_choice:
        print("🔧 Using SQL tool...")
        answer = sql_query_tool.invoke(question)
        
    else:  # rag
        print("🔧 Using RAG tool...")
        answer = rag_search_tool.invoke(question)
    
    return answer