from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

import db_init
db_init.init_db()


DATABASE = 'savez_quiz.db'

# Funkcija za povezivanje sa bazom
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return "Kviz backend je online! 🚀"

@app.route("/ping")
def ping():
    return jsonify({"status": "OK"}), 200

# Endpoint za slanje rezultata
@app.route('/submit', methods=['POST'])
def submit_score():
    data = request.get_json()
    username = data.get('username')
    score = data.get('score')

    if not username or score is None:
        return jsonify({"error": "Missing data"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO results (date, quiz, section, player)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), score, 'van_takmicenja', username))
    conn.commit()
    result_id = cur.lastrowid
    conn.close()

    share_url = f"https://kviz-baza-backend-1.onrender.com/share/{result_id}"
    return jsonify({"share_url": share_url}), 201

# Endpoint za rang listu svih vremena
@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    conn = get_db_connection()
    results = conn.execute('''
        SELECT player AS username, quiz AS score
        FROM results
        ORDER BY quiz DESC
        LIMIT 10
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in results])

# Endpoint za rang listu tekućeg meseca
@app.route('/leaderboard/month', methods=['GET'])
def leaderboard_month():
    now = datetime.now()
    month = now.strftime('%m')
    year = now.strftime('%Y')

    conn = get_db_connection()
    results = conn.execute('''
        SELECT player AS username, quiz AS score
        FROM results
        WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
        ORDER BY quiz DESC
        LIMIT 5
    ''', (month, year)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in results])

# Endpoint za rang listu tekuće godine
@app.route('/leaderboard/year', methods=['GET'])
def leaderboard_year():
    year = datetime.now().strftime('%Y')

    conn = get_db_connection()
    results = conn.execute('''
        SELECT player AS username, quiz AS score
        FROM results
        WHERE strftime('%Y', date) = ?
        ORDER BY quiz DESC
        LIMIT 10
    ''', (year,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in results])

# Endpoint za pojedinačan rezultat (za šerovanje)
@app.route('/result/<int:result_id>', methods=['GET'])
def result(result_id):
    conn = get_db_connection()
    row = conn.execute('''
        SELECT player AS username, quiz AS score, date
        FROM results
        WHERE id = ?
    ''', (result_id,)).fetchone()
    conn.close()

    if row:
        return jsonify({
            "username": row["username"],
            "score": row["score"],
            "timestamp": row["date"]
        })
    else:
        return jsonify({'error': 'Result not found'}), 404

@app.route('/results', methods=['GET'])
def all_results():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT id, date, quiz, section, player
        FROM results
        ORDER BY id DESC
    ''')
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/share/<int:result_id>', methods=['GET'])
def share(result_id):
    return result(result_id)
    
@app.route('/health', methods=['GET'])
def health():
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1')
        conn.close()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

@app.route('/result/top', methods=['GET'])
def result_top():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT player, quiz, section, date
        FROM results
        ORDER BY quiz DESC
        LIMIT 10
    ''')
    rows = cur.fetchall()
    conn.close()

    html = "<h2>Top 10 rezultata</h2><ol>"
    for row in rows:
        html += f"<li><strong>{row['player']}</strong> — {row['quiz']} poena ({row['section']}, {row['date']})</li>"
    html += "</ol>"
    return html

@app.route('/result/top30', methods=['GET'])
def result_top30():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT player, quiz, section, date
        FROM results
        WHERE section = 'prvih_30_dana'
        ORDER BY quiz DESC
        LIMIT 10
    ''')
    rows = cur.fetchall()
    conn.close()

    html = """
    <html>
    <head><title>Top 10 rezultata — Prvih 30 dana</title></head>
    <body>
    <h2>Top 10 rezultata za sekciju: <em>prvih_30_dana</em></h2>
    <ol>
    """
    for row in rows:
        html += f"<li><strong>{row['player']}</strong> — {row['quiz']} poena ({row['date']})</li>"
    html += """
    </ol>
    </body>
    </html>
    """
    return html

@app.route('/competition/register', methods=['POST'])
def register_for_competition():
    data = request.get_json()
    player = data.get('player')

    if not player:
        return jsonify({'error': 'Nedostaje ime igrača'}), 400

    # Možeš dodati logiku da proveriš da li je već prijavljen
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO results (date, quiz, section, player)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0, 'arena_prijava', player))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Igrač {player} je prijavljen u arenu'}), 201

# Pokretanje servera
if __name__ == '__main__':
    app.run(debug=True)


