import sqlite3

DATABASE = 'savez_quiz.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            quiz REAL NOT NULL,
            section TEXT,
            player TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Baza uspešno inicijalizovana.")


