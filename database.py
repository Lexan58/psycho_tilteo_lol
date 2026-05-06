import sqlite3

def connect_db():
    return sqlite3.connect("data/tilteo.db")

def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        champion TEXT,
        role TEXT,
        kda TEXT,
        result TEXT,
        tilt_level INTEGER,
        note TEXT
    )
    """)

    conn.commit()
    conn.close()

def get_last_champion_played():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT champion
        FROM matches
        ORDER BY id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    return None

def create_mental_log_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mental_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            score REAL,
            state TEXT
        )
    """)

    conn.commit()
    conn.close()

from datetime import datetime

def save_mental_state(score, state):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO mental_log (timestamp, score, state)
        VALUES (?, ?, ?)
    """, (datetime.now().isoformat(), score, state))

    conn.commit()
    conn.close()

def show_mental_log():
    conn = connect_db()
    cursor = conn.cursor()

    # Seleccionamos los últimos 10 registros para no llenar la pantalla
    cursor.execute("""
        SELECT timestamp, score, state 
        FROM mental_log 
        ORDER BY id DESC 
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_mental_timeline():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, score
        FROM mental_log
        ORDER BY timestamp
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_recent_mental_states(limit=5):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT score, state
        FROM mental_log
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows
