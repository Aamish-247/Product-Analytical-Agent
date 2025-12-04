import dspy
import json
import random
from dspy.teleprompt import BootstrapFewShot
from dspy_signatures import  generate_sql_query
from Router.sqlite_tool import fetch_info , execute_query
from rich.console import Console


console = Console()

info = fetch_info()


def load_training_data(file_path = "D:\\Assignment\\agents\\training_data.json"):
    with open(file_path, "r") as f:
        data = json.load(f)

    training_data= []

    for t in data:
        example = dspy.Example(
            query = t["query"],
            constraints = t["constraints"],
            db_schema = info,
            sql_generated_query = t["sql_generated_query"]
        ).with_inputs("query","constraints","db_schema")

        training_data.append(example)

    return training_data    

def check_execution_value(example , prediction , trace = None):
    """It will check the actual return of sql generator. if yes then then return 1 and otherwise return 0."""

    result = execute_query(prediction.sql_generated_query)
    results = result.lower()

    if "sql_error:" not in results and "returned no results" not in results:
        return 1.0
    return 0.0


def optimized_nl_to_sql():
    """it will optimized our nl_to_sql(query_generator) module."""

    training_data = load_training_data()
    random.shuffle(training_data)

    train = training_data[:int(len(training_data) * 0.8)]

    unoptimized_model = dspy.ChainOfThought(generate_sql_query)

    teleprompter = BootstrapFewShot(metric=check_execution_value,       
    max_bootstrapped_demos=3,max_labeled_demos=2)
 
    console.print("[bold yellow]Starting DSPy Optimization (BootstrapFewShot)...[/bold yellow]")

    optimized_model = teleprompter.compile(
        unoptimized_model,
        trainset=train
    )

    console.print("[bold green]DSPy Optimization Complete.[/bold green]")

    optimized_model.save("optimized_nl_to_sql.json")

    return optimized_model

if __name__ == '__main__':
    LLM_NAME="phi3.5:3.8b-mini-instruct-q4_K_M"

    lm = dspy.LM(f"ollama/{LLM_NAME}" , api_base ="http://localhost:11434")

    dspy.configure(lm = lm)

    optimized_model = optimized_nl_to_sql()
    print("optimized model and saved ")