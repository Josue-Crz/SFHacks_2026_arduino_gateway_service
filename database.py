import os
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

_conn = None


def get_db_connection():
    """Return a reusable psycopg2 connection using SUPABASE_DB_URL from .env."""
    global _conn
    if _conn is not None and not _conn.closed:
        return _conn

    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        raise RuntimeError("SUPABASE_DB_URL not set — add it to your .env file")

    _conn = psycopg2.connect(db_url)
    _conn.autocommit = True

    # Ensure the readings table exists (matches existing Supabase schema)
    with _conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id BIGSERIAL PRIMARY KEY,
                temperature NUMERIC NOT NULL,
                humidity NUMERIC NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
    return _conn


def _serialize_row(row):
    """Convert a RealDictRow to a JSON-safe dict (Decimal→float, datetime→str)."""
    result = dict(row)
    for k, v in result.items():
        if isinstance(v, Decimal):
            result[k] = float(v)
        elif isinstance(v, datetime):
            result[k] = v.isoformat()
    return result


def store_reading(temperature_f, humidity):
    """INSERT a sensor reading (temperature in F) and return the inserted row as a dict."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """INSERT INTO readings (temperature, humidity)
               VALUES (%s, %s) RETURNING *;""",
            (round(temperature_f, 2), round(humidity, 2)),
        )
        return _serialize_row(cur.fetchone())


def get_latest_reading():
    """SELECT the most recent reading, or None if the table is empty."""
    conn = get_db_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM readings ORDER BY created_at DESC LIMIT 1;")
        row = cur.fetchone()
        if row is None:
            return None
        return _serialize_row(row)
