# core/database.py
import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join("data", "tilteo.db")

def connect_db():
    return sqlite3.connect(DB_PATH)

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id TEXT UNIQUE,
        date TEXT,
        champion TEXT,
        role TEXT,
        kda TEXT,
        kills INTEGER DEFAULT 0,
        deaths INTEGER DEFAULT 0,
        assists INTEGER DEFAULT 0,
        result TEXT,
        tilt_level INTEGER DEFAULT 0,
        note TEXT DEFAULT '',
        is_analyzed INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

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

def match_exists(match_id: str) -> bool:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM matches WHERE match_id = ?", (match_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def save_match_to_db(stats: dict):
    query = """
    INSERT OR IGNORE INTO matches (
        match_id, date, champion, role, kda, kills, deaths, assists, result, tilt_level, is_analyzed
    ) VALUES (
        :match_id, :date, :champion, :role, :kda, :kills, :deaths, :assists, :result, 0, 0
    )
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, stats)
    conn.commit()
    conn.close()

def update_match_tilt(match_id: str, tilt_level: int, note: str):
    """Permite al usuario calificar emocionalmente una partida guardada por Riot."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE matches 
        SET tilt_level = ?, note = ? 
        WHERE match_id = ?
    """, (tilt_level, note, match_id))
    conn.commit()
    conn.close()

def get_matches_dataframe() -> pd.DataFrame:
    """Centraliza la lectura para evitar conexiones directas en analytics.py"""
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM matches ORDER BY id DESC", conn)
    conn.close()
    return df

def get_recent_tilt_data(last_n=5):
    """Migrado desde tilt_rules para unificar el acceso a datos."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tilt_level, result
        FROM matches
        ORDER BY id DESC
        LIMIT ?
    """, (last_n,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None, 0

    tilt_levels = [r[0] for r in rows if r[0] is not None]
    avg_tilt = sum(tilt_levels) / len(tilt_levels) if tilt_levels else 0

    losses_in_row = 0
    for r in rows:
        if r[1] == "Loss":  # Mapeado a tu string 'Loss'
            losses_in_row += 1
        else:
            break

    return avg_tilt, losses_in_row

def get_last_champion_played():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT champion FROM matches ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

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
    cursor.execute("SELECT timestamp, score, state FROM mental_log ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_mental_timeline():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, score FROM mental_log ORDER BY timestamp")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_recent_mental_states(limit=5):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT score, state FROM mental_log ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_champion_mental_stats():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT champion, AVG(tilt_level), COUNT(*)
        FROM matches
        WHERE tilt_level IS NOT NULL AND tilt_level > 0
        GROUP BY champion
        HAVING COUNT(*) >= 1
    """)
    data = cursor.fetchall()
    conn.close()
    return data