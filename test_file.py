from Router.sqlite_tool import fetch_info, execute_query
from Router.retrieval import retriever_documents

print("--- Testing Database ---")
print("Schema Preview:", fetch_info()[:200]) 
print("SQL Test:", execute_query("SELECT COUNT(*) FROM Products;"))

print("\n--- Testing RAG ---")
results = retriever_documents("return policy for beverages")
for res in results:
    print(f"Found: {res['id']} -> {res['text'][:50]}...")