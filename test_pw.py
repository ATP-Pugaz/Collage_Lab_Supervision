import mysql.connector

passwords = ["", "root", "admin", "password", "123456", "mysql"]

for pw in passwords:
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=pw
        )
        print(f"SUCCESS: Password is '{pw}'")
        conn.close()
        break
    except mysql.connector.Error as err:
        print(f"FAILED: Password '{pw}' - {err}")
