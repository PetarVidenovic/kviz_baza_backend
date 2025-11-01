import sqlite3

# Povezivanje sa bazom (kreira fajl ako ne postoji)
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Kreiranje tabele za rezultate
c.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    score REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("✅ Baza je uspešno kreirana.")
