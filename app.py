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
        LIMIT 10
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

# Pokretanje servera
if __name__ == '__main__':
    app.run(debug=True)


