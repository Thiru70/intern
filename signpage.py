from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import mysql.connector

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yourpassword",
    database="auth_db"
)
cursor = db.cursor()

# Create users table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    )
""")
db.commit()


@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data["email"]
    password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400


@app.route("/signin", methods=["POST"])
def signin():
    data = request.json
    email = data["email"]
    password = data["password"]

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user[2], password):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"error": "Invalid credentials"}), 401


if __name__ == "__main__":
    app.run(debug=True)
