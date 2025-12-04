import dspy
import json
import random
import os
from dspy.teleprompt import BootstrapFewShot
from rich.console import Console
from dspy_signatures import query_route
from dspy import Predict


console = Console()

def check_route_accuracy(example , prediction , trace = None):
    """it will predict the route with target route."""

    return 1.0 if prediction.route.strip().lower() == example.route.strip().lower() else 0.0


def load_training_data():
    """it will load training data for optimization process."""

    return [
        dspy.Example(query="According to the product policy, what is the return window (days) for unopened Beverages?", route="rag").with_inputs('query'),
        dspy.Example(query="During 'Summer Beverages 1997 as defined in the marketing calendar, which product category had the highest total quantity sold?", route="hybrid").with_inputs('query'),
        dspy.Example(query="Using the AOV definition from the KPI docs, what was the Average Order Value during 'Winter Classics 1997'?", route="hybrid").with_inputs('query'),
        dspy.Example(query="Top 3 products by total revenue all-time.", route="sql").with_inputs('query'),
        dspy.Example(query="Total revenue from the 'Beverages category during 'Summer Beverages 1997 dates.", route="hybrid").with_inputs('query'),
        dspy.Example(query="Per the KPI definition of gross margin, who was the top customer by gross margin in 1997? Assume CostOfGoods is approximated by 70% of UnitPrice if not available.", route="hybrid").with_inputs('query'),
    ]


def route_optimization():
    """it will optimized the query route."""

    train_data = load_training_data()

    train = train_data

    unoptimized_route = dspy.ChainOfThought(query_route)

    teleprompter = BootstrapFewShot(metric= check_route_accuracy,
    max_bootstrapped_demos = 2,max_labeled_demos = 1)

    console.print("[bold yellow]Starting DSPy Router Optimization...[/bold yellow]")

    optimized_route = teleprompter.compile(
        unoptimized_route,
        trainset=train
    )

    optimized_route.save("optimized_route.json")
    console.print("[bold green]Router Optimization Complete. Weights saved to optimized_router.json.[/bold green]")
    return optimized_route



if __name__ == '__main__':

    LLM_NAME = "phi3.5:3.8b-mini-instruct-q4_K_M"
    lm = dspy.LM(f"ollama/{LLM_NAME}", api_base="http://localhost:11434")
    dspy.configure(lm=lm)

    route_optimization()