"""
AI Chatbot Backend — Flask + SQLite + Google Gemini API

Final year project: full-stack AI chatbot with user authentication
and persistent chat history.

Setup:
    pip install -r requirements.txt
    set GEMINI_API_KEY environment variable (see README)

Run:
    python app.py
"""

import os
import sqlite3
from datetime import datetime

from flask import Flask, request, jsonify, session, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai

# ---------------------------------------------------------
# App setup
# ---------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-this")
CORS(app, supports_credentials=True)

DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot.db")

# Configure Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash") if GEMINI_API_KEY else None


# ---------------------------------------------------------
# Database helpers
# ---------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if they don't already exist. Run once on startup."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,         -- 'user' or 'assistant'
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

# ---------------------------------------------
# Home Route
# ---------------------------------------------
@app.route("/")
def home():
    return jsonify({
        "message": "AI Chatbot Backend Running Successfully"
    })

# ---------------------------------------------------------
# Auth routes
# ---------------------------------------------------------
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        return jsonify({"error": "Username already taken"}), 409

    password_hash = generate_password_hash(password)
    db.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash, datetime.utcnow().isoformat()),
    )
    db.commit()

    return jsonify({"message": "Account created successfully. Please log in."}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify({"message": "Login successful", "username": user["username"]}), 200


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200


@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"logged_in": False}), 200
    return jsonify({"logged_in": True, "username": session["username"]}), 200


# ---------------------------------------------------------
# Chat routes
# ---------------------------------------------------------
def require_login():
    return "user_id" in session


@app.route("/api/chat", methods=["POST"])
def chat():
    if not require_login():
        return jsonify({"error": "Please log in first"}), 401

    if model is None:
        return jsonify({"error": "Server is missing GEMINI_API_KEY. See README for setup."}), 500

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    user_id = session["user_id"]
    db = get_db()

    # Save user's message
    db.execute(
        "INSERT INTO chat_history (user_id, role, message, created_at) VALUES (?, ?, ?, ?)",
        (user_id, "user", user_message, datetime.utcnow().isoformat()),
    )
    db.commit()

    # Build conversation context from history (last 10 messages) so Gemini has memory
    rows = db.execute(
        "SELECT role, message FROM chat_history WHERE user_id = ? ORDER BY id DESC LIMIT 10",
        (user_id,),
    ).fetchall()
    rows = list(reversed(rows))  # oldest first

    gemini_history = []
    for row in rows[:-1]:  # exclude the message we just added; sent separately below
        gemini_role = "model" if row["role"] == "assistant" else "user"
        gemini_history.append({"role": gemini_role, "parts": [row["message"]]})

    try:
        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(user_message)
        ai_reply = response.text
    except Exception as e:
        return jsonify({"error": f"AI service error: {str(e)}"}), 502

    # Save AI's reply
    db.execute(
        "INSERT INTO chat_history (user_id, role, message, created_at) VALUES (?, ?, ?, ?)",
        (user_id, "assistant", ai_reply, datetime.utcnow().isoformat()),
    )
    db.commit()

    return jsonify({"reply": ai_reply}), 200


@app.route("/api/history", methods=["GET"])
def history():
    if not require_login():
        return jsonify({"error": "Please log in first"}), 401

    db = get_db()
    rows = db.execute(
        "SELECT role, message, created_at FROM chat_history WHERE user_id = ? ORDER BY id ASC",
        (session["user_id"],),
    ).fetchall()

    return jsonify({
        "history": [dict(row) for row in rows]
    }), 200


@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    if not require_login():
        return jsonify({"error": "Please log in first"}), 401

    db = get_db()
    db.execute("DELETE FROM chat_history WHERE user_id = ?", (session["user_id"],))
    db.commit()
    return jsonify({"message": "History cleared"}), 200


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)