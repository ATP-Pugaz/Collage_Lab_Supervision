import sqlite3
import os

DB_NAME = 'labms.db'

def setup():
    # Remove existing database to start fresh if needed
    # if os.path.exists(DB_NAME):
    #     os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("Creating tables...")
    
    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('user', 'admin')) DEFAULT 'user'
    )
    """)

    # Create Lab Usage table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        lab_name TEXT NOT NULL,
        staff_name TEXT NOT NULL,
        class TEXT NOT NULL,
        department TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """)

    # Insert initial data
    print("Inserting example users...")
    users_data = [
        ('admin', 'admin123', 'admin'),
        ('john', 'john123', 'user'),
        ('Nithya', 'Nithya001', 'user'),
        ('Rakshana', 'rakshana002', 'user'),
        ('Anitha', 'Anitha003', 'user'),
        ('Muruganandam', 'MuruAdmin01', 'admin'),
        ('Muthupondi', 'MuthuAdmin02', 'admin'),
        ('Nehru', 'NehruAdmin03', 'admin')
    ]

    for username, password, role in users_data:
        try:
            cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
                           (username, password, role))
        except sqlite3.Error as e:
            print(f"Error inserting {username}: {e}")

    conn.commit()
    conn.close()
    print(f"Database setup complete! File created: {DB_NAME}")

if __name__ == "__main__":
    setup()
