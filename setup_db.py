import mysql.connector
from mysql.connector import errorcode

import os

# Database configuration
db_config = {
    "host": os.environ.get("MYSQLHOST", "localhost"),
    "user": os.environ.get("MYSQLUSER", "root"),
    "password": os.environ.get("MYSQLPASSWORD", "Pugaz2006@atp"),
    "database": os.environ.get("MYSQLDATABASE", "labms"),
    "port": int(os.environ.get("MYSQLPORT", 3306))
}

DB_NAME = db_config["database"]

TABLES = {}
TABLES['users'] = (
    "CREATE TABLE `users` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `username` varchar(50) UNIQUE NOT NULL,"
    "  `password` varchar(255) NOT NULL,"
    "  `role` enum('user', 'admin') DEFAULT 'user',"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB"
)

TABLES['lab_usage'] = (
    "CREATE TABLE `lab_usage` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `user_id` int(11) NOT NULL,"
    "  `lab_name` varchar(100) NOT NULL,"
    "  `staff_name` varchar(100) NOT NULL,"
    "  `class` varchar(100) NOT NULL,"
    "  `department` varchar(100) NOT NULL,"
    "  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
    "  PRIMARY KEY (`id`),"
    "  KEY `user_id` (`user_id`),"
    "  CONSTRAINT `lab_usage_ibfk_1` FOREIGN KEY (`user_id`) "
    "     REFERENCES `users` (`id`) ON DELETE CASCADE"
    ") ENGINE=InnoDB"
)

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

def setup():
    try:
        cnx = mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return

    cursor = cnx.cursor()

    try:
        cursor.execute("USE {}".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

    # Insert initial data
    print("Inserting example users...")
    try:
        users_data = [
            ('admin', 'admin123', 'admin'),
            ('john', 'john123', 'user'),
            ('Nithya', 'Nithya001', 'user'),
            ('Rakshana', 'rakshana002', 'user'),
            ('Anitha', 'Anitha003', 'user'),
            ('Muruganandam', 'MuruAdmin01', 'admin'),
            ('Muthupondi', 'MuthuAdmin02', 'admin'),
            ('Nehru', 'NehruAdmin03', 'admin')
        ]
        cursor.executemany(
            "INSERT IGNORE INTO users (username, password, role) VALUES (%s, %s, %s)",
            users_data
        )
        cnx.commit()
        print("Example users inserted.")
    except mysql.connector.Error as err:
        print(f"Error inserting users: {err.msg}")

    cursor.close()
    cnx.close()
    print("Database setup complete.")

if __name__ == "__main__":
    setup()
