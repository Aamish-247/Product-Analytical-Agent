import sqlite3
import pandas as pd
import os

DB_Connection = os.path.join(os.path.dirname(__file__), "../data/northwind.sqlite")

if not os.path.exists(DB_Connection):
    print(f"Error: Database file not found at {DB_Connection}") 


def fetch_info():
    """ Fetche the information of database file. So that agent  will write correct SQL query."""

    Target_table = [
        "Orders", 
        "Order Details", 
        "Products", 
        "Categories", 
        "Customers"
    ]

    connection = sqlite3.connect(DB_Connection)
    cursor = connection.cursor()

    schema_info = ""

    for table in Target_table:
        try:
            cursor.execute(f"PRAGMA table_info(\"{table}\");")
            columns = cursor.fetchall()

            if columns:
                column_names = [col[1] for col in columns]
                schema_info += f"Table: {table}\nColumns: {','.join(column_names)}\n"

            # Fetch Foreign Keys
            cursor.execute(f"PRAGMA foreign_key_list(\"{table}\");")
            fks = cursor.fetchall()
            if fks:
                fk_info = [f"{fk[3]} -> {fk[2]}.{fk[4]}" for fk in fks]
                schema_info += f"Foreign Keys: {', '.join(fk_info)}\n"
            
            schema_info += "\n"

        except Exception as e:
            continue
    connection.close()
    return schema_info    
    

def execute_query(query: str):
    """Execute the given query and return the results"""

    try:
        connection = sqlite3.connect(DB_Connection)
        data = pd.read_sql_query(query, connection)
        connection.close()
    
        if data.empty:
            return "Query executed but returned empty results."
    
        result = data.to_string(index=False)
        return result

    except Exception as e:
        return f" Error executing query: {str(e)}"
