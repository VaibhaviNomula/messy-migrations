import sqlite3
from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Drop existing table if it exists
cursor.execute('DROP TABLE IF EXISTS users')

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# Insert sample data with hashed passwords
sample_users = [
    ('John Doe', 'john@example.com', hash_password('password123')),
    ('Jane Smith', 'jane@example.com', hash_password('secret456')),
    ('Bob Johnson', 'bob@example.com', hash_password('qwerty789'))
]

cursor.executemany(
    "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
    sample_users
)

conn.commit()
conn.close()

print("Database initialized with sample data")
