import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="sigp",
        user="postgres",
        password="tu_password"
    )
    return conn

def fetch_properties():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM properties;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows