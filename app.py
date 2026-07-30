from flask import Flask, request, jsonify, render_template
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()  # يقرأ المتغيرات من ملف .env

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

# خريطة تحويل اسم الزرار إلى الحرف المطلوب تخزينه
COMMAND_MAP = {
    "forward": "f",
    "backward": "b",
    "left": "l",
    "right": "r",
    "stop": "S"
}


def get_db_connection():
    return psycopg.connect(DATABASE_URL)


def init_db():
    """ينشئ الجداول أول مرة لو مش موجودة، ويحط قيمة ابتدائية"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS robot_state (
            id INTEGER PRIMARY KEY,
            command TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS voice_notes (
            id SERIAL PRIMARY KEY,
            text_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # نتأكد إن الصف رقم 1 موجود بجدول robot_state
    cur.execute("SELECT * FROM robot_state WHERE id = 1")
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO robot_state (id, command) VALUES (1, 'S')")

    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/voice")
def voice_page():
    return render_template("voice.html")


@app.route("/update_command", methods=["POST"])
def update_command():
    button = request.form.get("command", "")

    if button not in COMMAND_MAP:
        return jsonify({"status": "error", "message": "أمر غير معروف"}), 400

    letter = COMMAND_MAP[button]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE robot_state SET command = %s, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
        (letter,)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success", "button": button, "stored_as": letter})


@app.route("/get_state", methods=["GET"])
def get_state():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT command, updated_at FROM robot_state WHERE id = 1")
    row = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify({"command": row[0], "updated_at": str(row[1])})


@app.route("/save_voice", methods=["POST"])
def save_voice():
    text = request.form.get("text", "").strip()

    if not text:
        return jsonify({"status": "error", "message": "النص فاضي"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO voice_notes (text_content) VALUES (%s)",
        (text,)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success", "saved_text": text})


@app.route("/get_voice_notes", methods=["GET"])
def get_voice_notes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, text_content, created_at FROM voice_notes ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    notes = [
        {"id": row[0], "text_content": row[1], "created_at": str(row[2])}
        for row in rows
    ]
    return jsonify(notes)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)