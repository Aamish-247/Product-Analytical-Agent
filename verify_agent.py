from agents.graph_hybrid import app, Agent_State
from rich.console import Console
import json

console = Console()

query = "What is the total sales amount for customers in Germany?"
format_hint = "Return the total amount as a float."

print(f"Query: {query}")

initial_state = Agent_State(
    query=query,
    format_hint=format_hint,
    route="sql",
    context=[],
    sql_query="",
    sql_error="",
    sql_result="",
    iteration=0,
    confidence=0.0
)

try:
    final_state = app.invoke(initial_state)
    print("\n--- FINAL STATE ---")
    print(f"SQL Query: {final_state.get('sql_query')}")
    print(f"SQL Result: {final_state.get('sql_result')}")
    print(f"Final Info: {final_state.get('final_ans')}")
    print(f"Citations: {final_state.get('citation')}")
except Exception as e:
    console.print_exception()
