import os
import sqlite3
import openai
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Initialize Flask App
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# OpenAI API Key (replace with your own)
openai.api_key = "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"

# Database Connection
def get_db_connection():
    conn = sqlite3.connect("repository.db")
    conn.row_factory = sqlite3.Row
    return conn

# Check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Home Route
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Digital Resource Repository!"})

# 📂 Upload Document Route
@app.route("/api/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    title = request.form.get("title")
    category = request.form.get("category")

    if file.filename == "" or not title or not category:
        return jsonify({"error": "Missing file, title, or category"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO documents (title, filename, category) VALUES (?, ?, ?)",
            (title, filename, category),
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "File uploaded successfully!", "filename": filename}), 201
    else:
        return jsonify({"error": "Invalid file type"}), 400

# 🔍 Search Documents Route
@app.route("/api/search", methods=["GET"])
def search_documents():
    category = request.args.get("category")

    conn = get_db_connection()
    cursor = conn.cursor()

    if category:
        cursor.execute("SELECT * FROM documents WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM documents")

    documents = cursor.fetchall()
    conn.close()

    return jsonify([dict(doc) for doc in documents])

# 📜 AI-powered Summarization Route
@app.route("/api/summarize", methods=["POST"])
def summarize_document():
    data = request.json
    content = data.get("content")

    if not content:
        return jsonify({"error": "No content provided"}), 400

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Summarize this document."}, {"role": "user", "content": content}]
    )

    summary = response["choices"][0]["message"]["content"]
    
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)
