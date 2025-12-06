# Retail Analytics Agent

A hands-on practice work on a powerful hybrid AI agent designed to provide analytical insights by querying both unstructured documents (via RAG) and structured databases (via SQL).

## Overview

The Retail Analytics Agent leverages advanced techniques including LangGraph for workflow orchestration and DSPy for optimized prompt engineering. It intelligently routes user queries to the most appropriate data source:
- **RAG (Retrieval Augmented Generation)**: For general knowledge or specific documentation.
- **SQL**: For quantitative analysis on the Northwind database.
- **Hybrid**: For complex queries requiring both structured and unstructured context.

## Model Information

The agent utilizes the **`phi3.5:3.8b-mini-instruct-q4_K_M`** model via Ollama. This lightweight yet powerful model ensures efficient processing while maintaining high accuracy.

## Features

- **Intelligent Routing**: Automatically classifies queries to determine the best execution path.
- **Self-Correcting SQL**: Generates SQL queries and automatically repairs them if execution fails.
- **Document Retrieval**: Retrieves relevant context from indexed documents.
- **Comprehensive Analysis**: Synthesizes answers using both database results and document context.
- **Confidence Scoring**: Provides a confidence score for generated answers.

## Architecture

The agent follows a graph-based architecture:
1. **Router**: Analyzes the query to decide the strategy (RAG, SQL, or Hybrid).
2. **Retriever**: Fetches relevant documents if needed.
3. **Planner**: Extracts constraints and plans the SQL query logic.
4. **SQL Generator**: Converts natural language to SQL using schema information.
5. **Execution**: Runs the query against the SQLite database.
6. **Synthesize**: Combines all gathered information to generate the final response with citations.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <https://github.com/Aamish-247/Product-Analytical-Agent>
   cd Assignment
   ```

2. **Set up Virtual Environment:**
   It is recommended to use a virtual environment to manage dependencies.
   ```bash
   # Create virtual environment
   python -m venv myenv

   # Activate virtual environment (Windows)
   myenv\Scripts\activate
   ```

3. **Install dependencies:**
   Make sure you have Python 3.10+ installed.
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the Model:**
   The agent requires a specific Ollama model to function. Run the following command to download it internally to your Ollama registry:
   ```bash
   ollama pull phi3.5:3.8b-mini-instruct-q4_K_M
   ```

5. **Database Setup:**
   Ensure the `northwind.sqlite` file is present in the `data/` directory.

## Usage

Run the agent using the command line interface:

```bash
python run_agent_hybrid.py --batch <sample_questions_hybrid_eval.jsonl> --out <outputs_hybrid.jsonl>
```

### Arguments:
- `--batch`: Path to the input JSONL file containing queries.
- `--out`: Path to save the results in JSONL format.

### Input File Format:
Each line in the input JSONL should look like:
```json
{"id": "q1", "question": "How many orders were placed in 2023?", "format_hint": "number"}
```

## Project Structure

```text
Product-Analytical-Agent/
├── agents/
│   ├── dspy_signatures.py    # DSPy signatures for prompts
│   └── graph_hybrid.py       # Main LangGraph workflow
├── data/
│   └── northwind.sqlite      # SQLite database
├── docs/
│   |── catalog.md
│   ├── kpi_defination.md        
│   └── product_policy.md
├── Router/
│   ├── retrieval.py          # RAG retrieval logic
│   └── sqlite_tool.py        # Database interaction tools
├── run_agent_hybrid.py       # CLI entry point
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Contribution

We welcome contributions! Please follow these steps to contribute:

1. **Fork the repository** to your own GitHub account.
2. **Clone the fork** to your local machine.
3. **Create a new branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
4. **Commit your changes** with descriptive commit messages:
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
5. **Push to the branch**:
   ```bash
   git push origin feature/AmazingFeature
   ```
6. **Open a Pull Request** against the main repository.
