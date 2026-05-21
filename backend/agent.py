from langchain.agents import AgentExecutor, create_react_agent  # ← Changed
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate  # ← Changed
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

def create_agent():
    """Create LangChain ReAct agent with SQL and RAG tools"""
    
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
    
    # Define tools
    tools = [sql_query_tool, rag_search_tool]
    
    # Create ReAct prompt template
    template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

    prompt = PromptTemplate.from_template(template)
    
    # Create agent
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    
    return agent_executor

def ask_agent(question: str) -> str:
    """Ask the agent a question"""
    agent = create_agent()
    result = agent.invoke({"input": question})
    return result["output"]