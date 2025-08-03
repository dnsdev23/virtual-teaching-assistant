#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('virtual_ta.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# 檢查是否有 rag_query_logs 表
if ('rag_query_logs',) in tables:
    cursor.execute("SELECT COUNT(*) FROM rag_query_logs;")
    count = cursor.fetchone()[0]
    print(f"RAG query logs count: {count}")
    
    cursor.execute("PRAGMA table_info(rag_query_logs);")
    columns = cursor.fetchall()
    print("RAG query logs table structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()
print("Database check complete!")
