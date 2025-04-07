import sqlite3

# Connect to database
conn = sqlite3.connect('database.db')

# Create a cursor
cursor = conn.cursor()

# Create the bone_experts table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bone_experts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    password TEXT,
    mobile TEXT,
    address TEXT,
    hospital TEXT,
    qualification TEXT,
    specialization TEXT
)
''')

# Commit and close
conn.commit()
conn.close()

print("Table 'bone_experts' created successfully.")
