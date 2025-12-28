from flask import Flask, render_template, request, redirect, session, url_for
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Read SECRET_KEY from .env
app.secret_key = os.getenv("SECRET_KEY")

# Read DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """
    Connect to Supabase PostgreSQL using SSL.
    """
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not set in environment or .env file!")
        return None
    try:
        conn = connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as err:
        print(f"❌ Database Connection Error: {err}")
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
            return "❌ Database connection failed. Check DATABASE_URL."

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            error = "Username not found"
        elif user["password"] != password:  # ⚠ Add hashing later
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

    # Admin view
    if session.get("role") == "admin":
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            query = """
                SELECT lu.*, u.username
                FROM lab_usage lu
                JOIN users u ON lu.user_id = u.id
                WHERE lu.updated_at > NOW() - INTERVAL '3 hours'
                ORDER BY lu.updated_at DESC
            """

            cursor.execute(query)
            data = cursor.fetchall()

            cursor.close()
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
        return "❌ Database connection failed."

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO lab_usage (user_id, lab_name, staff_name, class, department)
        VALUES (%s, %s, %s, %s, %s)
    """, (session["user_id"], lab_name, staff_name, student_class, department))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("home", message="✅ Updated successfully!"))


@app.route("/logout")
def logout():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lab_usage")
        conn.commit()
        cursor.close()
        conn.close()

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
