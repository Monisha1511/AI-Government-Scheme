import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="hari1234",   # change this
        database="gov_scheme_ai"
    )

def fetch_all_schemes():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM schemes")
    schemes = cursor.fetchall()
    conn.close()
    return schemes