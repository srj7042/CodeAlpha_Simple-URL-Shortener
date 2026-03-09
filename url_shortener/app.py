from flask import Flask, request, redirect, jsonify, render_template
import sqlite3
import string
import random
app = Flask(__name__)
def init_db():
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE,
            long_url TEXT
        )
    """)
    conn.commit()
    conn.close()
init_db()
def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/shorten", methods=["POST"])
def shorten_url():

    data = request.get_json()
    long_url = data.get("url")

    if not long_url:
        return jsonify({"error": "URL is required"}), 400

    short_code = generate_code()
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO urls (short_code, long_url) VALUES (?, ?)",
        (short_code, long_url)
    )
    conn.commit()
    conn.close()

    short_url = f"http://127.0.0.1:5000/{short_code}"

    return jsonify({
        "long_url": long_url,
        "short_url": short_url
    })
@app.route("/<short_code>")
def redirect_url(short_code):
    conn = sqlite3.connect("urls.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT long_url FROM urls WHERE short_code=?",
        (short_code,)
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        return redirect(result[0])
    else:
        return " URL not found"
if __name__ == "__main__":
    app.run(debug=True)