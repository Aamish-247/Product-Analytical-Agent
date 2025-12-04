import click
import json
import os
from agents.graph_hybrid import app , Agent_State
from rich.console import Console

console = Console()

def run_agent(query:str , format_hint: str, route: str):
    """it will start the agent and analyze the query"""

    initial_state = Agent_State(
        query=query,
        format_hint=format_hint,
        route = route,
        context = [],
        sql_query="",
        sql_error="",
        sql_result="",
        iteration=0,
        confidence=0.0
    )

    final_state = None

    try: 
        final_state = app.invoke(initial_state)
    except Exception as e:
        console.print(f"[bold red]CRITICAL ERROR RUNNING GRAPH:[/bold red] {e}")    
    return final_state

@click.command()
@click.option('--batch','batch_file', required=True, type=click.Path(exists=True))
@click.option('--out', 'output_file', required=True, type=click.Path())
def cli(batch_file, output_file):
    """Retail Analytics Agent CLI. """

    question = []

    try:
        with open(batch_file, 'r') as f:
            for line in f:
                if line.strip():
                    question.append(json.loads(line))
    except Exception as e:
        console.print(f"[bold red]Error loading batch file:[/bold red] {e}")
        return                

    output_results = []
    for o , item in enumerate(question):
        id = item['id']
        query = item["question"]
        format_hint = item["format_hint"]

        calculated_route = id.split("_")[0]

        console.rule(f"[bold yellow]Q {o+1}/{len(question)}: {id}[/bold yellow]")

        final_state = run_agent(query , format_hint, calculated_route)

        if final_state:
            try:
                citation_list = json.loads(final_state.get('citations','[]'))
            except json.JSONDecodeError:
                citation_list = ["Error Parsing."] 

            
            results = {
                "id": id,
                "final_answer":final_state.get('final_answer',""),
                "sql": final_state.get('sql_query', ''),
                "confidence": round(final_state.get('confidence', 0.0), 2),
                "explanation": f"Route: {final_state.get('route', 'N/A')}. Repairs: {final_state.get('iteration', 0)}.",
                "citations": citation_list
            }
            output_results.append(results) 
        else:
            output_results.append({
                "id": id,
                "final_answer": "Execution Failed",
                "sql": "",
                "confidence": 0.0,
                "explanation": "Critical failure.",
                "citations": []})
            
    with open(output_file, 'w', encoding= 'utf-8') as f:
        for I in output_results:
            f.write(json.dumps(I) + '\n')

    console.rule(f"[bold green]Successfully saved results to {output_file}[/bold green]")       


if __name__ == '__main__':
    cli()