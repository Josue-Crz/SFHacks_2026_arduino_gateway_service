import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Return a psycopg2 connection using SUPABASE_DB_URL from .env"""
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        raise ValueError(
            "SUPABASE_DB_URL not set — copy .env.example to .env and fill in your Supabase credentials"
        )
    return psycopg2.connect(db_url)

def store_reading(temperature, humidity):
    """Insert a sensor reading into the readings table. Returns the inserted row."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO readings (temperature, humidity) VALUES (%s, %s) RETURNING id, temperature, humidity, created_at;",
        (temperature, humidity)
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return {
        "id": row[0],
        "temperature": float(row[1]),
        "humidity": float(row[2]),
        "created_at": row[3].isoformat()
    }

def get_latest_reading():
    """Fetch the most recent reading from the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, temperature, humidity, created_at FROM readings ORDER BY created_at DESC LIMIT 1;")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        return None
    return {
        "id": row[0],
        "temperature": float(row[1]),
        "humidity": float(row[2]),
        "created_at": row[3].isoformat()
    }
