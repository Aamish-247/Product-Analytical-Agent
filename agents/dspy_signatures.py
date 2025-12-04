import dspy

class query_route(dspy.Signature):
    """Classify the user query into one of three execution routes:
    1. 'rag': For questions about policies, definitions, or text documents (unstructured data).
    2. 'sql': For questions requiring calculations, statistics, or direct database lookups (structured data).
    3. 'hybrid': For questions needing both document context (e.g., specific dates/definitions) and database stats."""

    query :str = dspy.InputField(desc = "User Analytical Query")
    route: str = dspy.OutputField(desc = "Query Route: 'rag', 'sql', 'hybrid'")


class plan_sql_query(dspy.Signature):
    """Analyze the query and context to extract structured constraints for SQL generation.
    Do not generate SQL here, just extract the variables."""

    context:str = dspy.InputField(desc = "Context from documents defining rules, formulas, or business years (e.g., 'Summer 1997 is June to August')")
    query: str = dspy.InputField(desc = "User Analytical Query")

    date_range: str = dspy.OutputField(desc="Extracted date range in 'YYYY-MM-DD' format or 'all_time'. Example: '1997-06-01 AND 1997-06-30'")
    KPIs:str = dspy.OutputField(desc= "Logic or formulas for calculations. Example: 'GrossMargin = (Price - Cost) * Qty'")
    category: str = dspy.OutputField(desc = "Specific filters or entity names to query. Example: 'Beverages', 'Germany'")

class generate_sql_query(dspy.Signature):
    """Generate an executable SQLite query based on the schema and constraints. CRITICAL: Output ONLY the SQL string. Do not include markdown, explanations, or notes."""

    db_schema:str = dspy.InputField(desc = "Database schema containing Table names and Column names.")
    constraints:str = dspy.InputField(desc = "Filters, Date Ranges, and KPI formulas to apply.")
    query:str = dspy.InputField(desc = "User Analytical Query")

    sql_generated_query:str = dspy.OutputField(desc = "The final executable SQL query string only. Use double quotes for table names with spaces.")


class Synthesize_answer(dspy.Signature):
    """Synthesize a natural language answer based on the SQL result and Context.
    The answer must strictly follow the requested format."""

    query:str = dspy.InputField(desc = "Original User Query")
    format_hint: str = dspy.InputField(desc="Required output format (e.g., 'Return a single integer', 'Return a list of names').")
    context:str = dspy.InputField(desc = "Relevant text chunks from documents.")
    sql_result:str = dspy.InputField(desc= "Raw result returned from the database execution.")

    final_ans:str = dspy.OutputField(desc= "Final answer in the requested format.")
    citation:str = dspy.OutputField(desc= "A JSON list of strings containing ONLY the database Tables used in the SQL and the Document Chunk IDs relevant to the answer. Format: ['Orders', 'policies::chunk2']")
