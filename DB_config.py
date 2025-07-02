from config import DB_PORT, DB_NAME, DB_HOST, DB_PASSWORD, DB_USER
from flask import jsonify, Blueprint
import psycopg2
from psycopg2.extras import RealDictCursor

# Database Connection
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
        cursor_factory=RealDictCursor
    )
except Exception as e:
    print("Connection Failed: ", e)


cur = conn.cursor()