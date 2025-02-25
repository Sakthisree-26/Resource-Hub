import sqlite3

conn = sqlite3.connect("repository.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    category TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("Database Initialized!")
