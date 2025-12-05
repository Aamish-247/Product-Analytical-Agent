from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
import operator
import dspy
from dspy import Predict
from .dspy_signatures import query_route, plan_sql_query, generate_sql_query, Synthesize_answer
from Router.sqlite_tool import fetch_info, execute_query
from Router.retrieval import retriever_documents
import os
import json

LLM_NAME = "phi3.5:3.8b-mini-instruct-q4_K_M"

lm = dspy.LM(
    f"ollama/{LLM_NAME}",                 
    api_base="http://localhost:11434",          
)

dspy.configure(lm=lm)

class Agent_State(TypedDict):
    query:str
    format_hint:str
    route:str
    context: Annotated[List[str],operator.add]
    sql_query:str
    sql_result:str
    sql_error:str
    iteration:int
    confidence:float


route_query = Predict(query_route) 
sql_query_generator= Predict(generate_sql_query)
OPTIMIZED_SQL_PATH = "D:\\Assignment\\agents\\optimized_nl_to_sql.json"

if os.path.exists(OPTIMIZED_SQL_PATH):
    with open(OPTIMIZED_SQL_PATH, 'r', encoding='utf-8') as f:
        state = json.load(f)

        if "predict" in state:
            final_state = state['predict']  
        else:
            final_state = state.get('ChainOfThought', state)     

    sql_query_generator.load_state(final_state)
    print("Sql Path Loaded.")
else:
    print("Sql Path  file not found")    


query_planner = dspy.ChainOfThought(plan_sql_query)
answer_validation = dspy.ChainOfThought(Synthesize_answer)    

#Nodes

def query_route_node(state: Agent_State):
    """it will check the where the question will route."""

    if state['route'] in ['rag','sql','hybrid']:
        return{"route":state['route'], "iteration": 0}
    
    print("Route Not Founded. We are calling LLM")
    prediction = route_query(query=state['query'])
    return {"route" : prediction.route.strip().lower() , "iteration":0}



def retrieve_docs(state: Agent_State):
    """It will use RAG for retrieve documents"""

    query = state['query']
    context_list = []

    if state['route'] in ['rag','hybrid']:

        docs = retriever_documents(query)
        context_list.extend([f"Source Doc: {d['id']}\n Text:{d['text']}" for d in docs])

    # context_list = [f"Source Doc: {d['id']}\n Text:{d['text']}" for d in docs]

    if state['route'] in ['sql','hybrid']:
        info = fetch_info()
        context_list.append(f"DB info:{info}")

    return {"context":context_list, "iteration": state['iteration']}  



def planner_query(state: Agent_State):
    """it will extract constraints and all other necessary information for planing query"""

    context_str = "\n - \n".join(state['context'])

    plan_query = query_planner(context = context_str, query = state['query'])


    constraints = (
        f"Date Range: {plan_query.date_range}\n"
        f"KPIs: {plan_query.KPIs}\n"
        f"category: {plan_query.category}"
    )

    state['context'].append(f"Plan Constraints:\n{constraints}")
    return{"context":state['context'], "iteration":state['iteration']}

def query_generator(state:Agent_State):
    """it will generate final sql query"""
    info = [i for i in state['context'] if i.startswith("DB info:")] 
    constraints = [c for c in state['context'] if c.startswith("Plan Constraints:")]

    input_schema = info[0] if info else "DB Schema not found."

    sql_output = sql_query_generator(
        db_schema = input_schema,
        constraints = constraints[0] if constraints else "none",
        query = state['query']
    )

    clean_sql_query = sql_output.sql_generated_query.strip().replace("```sql","").replace("```","").strip()


    return{"sql_query": clean_sql_query, "iteration": state["iteration"]}

def query_execute(state: Agent_State):
    """query execution"""

    result = execute_query(state["sql_query"])

    if result.startswith("SQL Error:"):
        return{"sql_result": "" , "sql_error": result , "iteration":state["iteration"]}
    else:
        return{"sql_result": result , "sql_error": "" , "iteration": state["iteration"]}
    

def answer_analyzer_node(state:Agent_State):
    """it will analyze the final answer according to format_hint"""

    concat_context = ("\n".join([c for c in state["context"] if not c.startswith("DB Schema:")])+ f"\n DB Result:\n{state['sql_result']}")

    anaylze_answer = answer_validation(
        query = state["query"],
        format_hint = state['format_hint'],
        context = concat_context,
        sql_result = state['sql_result']
    )

    if state['sql_error'] or not state['sql_result']:
        confidence = 0.5
    else:
        confidence = 1.0

    return{"final_ans": anaylze_answer.final_ans.strip(),
           "citation": anaylze_answer.citation.strip(),
            "confidence": confidence,
            "iteration": state["iteration"]}


def repair_node(state: Agent_State):
    """checking the error."""

    if state["sql_error"] and state["iteration"]<2:
        return "repair"
    return "analyze_answer"


def route_validate(state: Agent_State):
    """decide the next step according route state"""
    if state["route"] == 'rag':
        return "only_rag"
    elif state["route"] == "sql":
        return "sql_start"
    elif state["route"] == "hybrid":
        return "hybrid_start"
    return "error"


def check_retriever_next_step(state:Agent_State):
    """check again if route is hybrid then move it to planner"""

    if state["route"] == "rag":
        return "synthesize"
    else:
        return "planner"

#Graph Building

workflow = StateGraph(Agent_State)

workflow.add_node("router", query_route_node)
workflow.add_node("retriever", retrieve_docs)
workflow.add_node("planner", planner_query)
workflow.add_node("nl_to_sql", query_generator)
workflow.add_node("Execution", query_execute)
workflow.add_node("synthesize", answer_analyzer_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges("router",route_validate,{
    "sql_start": "retriever",
    "hybrid_start": "retriever",
    "only_rag": "retriever",
    "error": END
})

workflow.add_conditional_edges("retriever",check_retriever_next_step,{
    "synthesize": "synthesize",
    "planner" : "planner"
})

workflow.add_edge("planner","nl_to_sql")
workflow.add_edge("nl_to_sql", "Execution")

workflow.add_conditional_edges("Execution",repair_node,{
    "repair":"nl_to_sql",
    "analyze_answer": "synthesize"
})

workflow.add_edge("synthesize", END)

app = workflow.compile()
