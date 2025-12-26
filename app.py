from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "secret_key_here")

DB_NAME = 'labms.db'

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        return conn
    except sqlite3.Error as err:
        print(f"Error: {err}")
        return None

@app.route("/", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))
        
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        if not conn:
            return "Database connection failed. Please run setup_sqlite.py first."
            
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            error = "Username not found"
        elif user["password"] != password:
            error = "Incorrect password"
        else:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("home"))

    return render_template("login.html", error=error)

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    message = request.args.get("message", "")
    data = []
    
    # If admin, fetch all recent lab usage data
    if session.get("role") == "admin":
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Fetch data from the last 3 hours
            # SQLite stores TIMESTAMP in UTC by default if using CURRENT_TIMESTAMP
            query = """
                SELECT lu.*, u.username 
                FROM lab_usage lu
                JOIN users u ON lu.user_id = u.id
                WHERE lu.updated_at >= DATETIME('now', '-3 hours')
                ORDER BY lu.updated_at DESC
            """
            cursor.execute(query)
            data = cursor.fetchall()
            conn.close()

    return render_template("home.html", message=message, data=data)

@app.route("/staff_update/<lab_name>")
def staff_update(lab_name):
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") == "admin":
        return redirect(url_for("home", message="Admins cannot update details."))
    return render_template("staff_update.html", lab_name=lab_name)

@app.route("/save_update", methods=["POST"])
def save_update():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") == "admin":
        return redirect(url_for("home", message="Admins cannot save updates."))

    lab_name = request.form["lab_name"]
    staff_name = request.form["staff_name"]
    student_class = request.form["class"]
    department = request.form["department"]

    conn = get_db_connection()
    if not conn:
        return "Database connection failed."
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO lab_usage (user_id, lab_name, staff_name, class, department) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], lab_name, staff_name, student_class, department)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home", message="✅ Updated successfully!"))

@app.route("/logout")
def logout():
    # Reset all data on logout (as per user's earlier requirement)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lab_usage")
        conn.commit()
        conn.close()
        
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
