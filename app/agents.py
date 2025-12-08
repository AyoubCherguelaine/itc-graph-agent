from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from app.graph import graph_db
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- State ---
class AgentState(TypedDict):
    question: str
    classification: str
    context: str
    answer: str

# --- Nodes ---

def classify_question(state: AgentState):
    """Classifies the question as 'graph' (ITC specific data) or 'general'."""
    question = state["question"]
    prompt = f"""
    You are a classifier for the 'ITC BLIDA' (ITCommunity Club) AI assistant.
    Determine if the user's question requires querying the Knowledge Graph about the club's internal data or if it is general conversation.
    
    Knowledge Graph covers:
    - Members/Employees (names, roles)
    - Departments (Development, Design, Marketing, Content Creation, HR)
    - Events (ITC TALKS, ITCup, WelcomeDay)
    - Projects/Workshops

    Respond with ONLY 'graph' or 'general'.
    
    Question: {question}
    """
    response = LLM.invoke([HumanMessage(content=prompt)])
    classification = response.content.strip().lower()
    # Fallback if LLM creates verbiage
    if "graph" in classification:
        return {"classification": "graph"}
    return {"classification": "general"}

def run_general_agent(state: AgentState):
    """Handles general chitchat."""
    question = state["question"]
    response = LLM.invoke([SystemMessage(content="You are a helpful assistant for ITC BLIDA, a scientific club at Saad Dahleb University."), HumanMessage(content=question)])
    return {"answer": response.content}

def run_graph_agent(state: AgentState):
    """Generates Cypher, queries Neo4j, and formulates an answer."""
    question = state["question"]
    
    # 1. Generate Cypher
    schema_desc = """
    Nodes: 
    - Member (id, name, role)  // 'Member' instead of 'Employee' for a club
    - Department (name)        // e.g. Development, Design, Marketing
    - Event (name, date)       // e.g. ITC TALKS, ITCup
    
    Relationships:
    - (:Member)-[:MEMBER_OF]->(:Department)
    - (:Member)-[:ORGANIZES]->(:Event)
    - (:Department)-[:HOSTS]->(:Event)
    """
    cypher_prompt = f"""
    Task: Generate a Cypher query for Neo4j to answer the question for ITC BLIDA club.
    Schema: {schema_desc}
    
    Question: {question}
    
    instructions:
    - RETURN only the relevant data.
    - Do NOT markdown format the query (no ```cypher).
    - Case insensitive search is safer (use toLower()).
    - Return ONLY the Cypher query text.
    - IMPORTANT: Node labels are 'Member', 'Department', 'Event'. 
    """
    
    cypher_response = LLM.invoke([HumanMessage(content=cypher_prompt)])
    query = cypher_response.content.strip().replace("```cypher", "").replace("```", "")
    
    print(f"DEBUG: Generated Query: {query}")
    
    # 2. Execute Query
    try:
        results = graph_db.query(query)
        context = str(results)
    except Exception as e:
        context = f"Error executing query: {e}"
        
    # 3. Formulate Answer
    answer_prompt = f"""
    You are the AI assistant for ITC BLIDA (ITCommunity Club at Saad Dahleb University).
    Question: {question}
    Database Results: {context}
    
    Formulate a concise, natural language answer based on the results. 
    If results are empty, say you couldn't find information in the club's records.
    """
    final_answer = LLM.invoke([HumanMessage(content=answer_prompt)])
    
    return {"answer": final_answer.content, "context": context}

# --- Router ---

def route_step(state: AgentState) -> Literal["graph_agent", "general_agent"]:
    if state["classification"] == "graph":
        return "graph_agent"
    return "general_agent"

# --- Graph Definition ---

workflow = StateGraph(AgentState)

workflow.add_node("classifier", classify_question)
workflow.add_node("graph_agent", run_graph_agent)
workflow.add_node("general_agent", run_general_agent)

workflow.set_entry_point("classifier")

workflow.add_conditional_edges(
    "classifier",
    route_step,
    {
        "graph_agent": "graph_agent",
        "general_agent": "general_agent"
    }
)

workflow.add_edge("graph_agent", END)
workflow.add_edge("general_agent", END)

agent_app = workflow.compile()
