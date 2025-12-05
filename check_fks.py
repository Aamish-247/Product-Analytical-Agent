import sqlite3
import os

db_path = "d:\\Assignment\\data\\northwind.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = ["Orders", "Order Details", "Products", "Categories", "Customers"]

print("Checking Foreign Keys:")
for table in tables:
    print(f"\n--- {table} ---")
    try:
        cursor.execute(f"PRAGMA foreign_key_list(\"{table}\")")
        fks = cursor.fetchall()
        if fks:
            for fk in fks:
                # id, seq, table, from, to, on_update, on_delete, match
                print(f"  FK to {fk[2]}: {fk[3]} -> {fk[4]}")
        else:
            print("  No FKs defined.")
    except Exception as e:
        print(f"  Error: {e}")

conn.close()
