import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path("runs.db")

def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with _conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                created_at TEXT,
                status TEXT,
                goal TEXT,
                result TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS run_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                event TEXT,
                created_at TEXT
            )
        """)

def create_run(run_id: str, goal: str):
    with _conn() as con:
        con.execute(
            "INSERT INTO runs (run_id, created_at, status, goal) VALUES (?, ?, ?, ?)",
            (run_id, datetime.now(timezone.utc).isoformat(), "running", goal)
        )

def append_event(run_id: str, event: dict):
    with _conn() as con:
        con.execute(
            "INSERT INTO run_events (run_id, event, created_at) VALUES (?, ?, ?)",
            (run_id, json.dumps(event), datetime.now(timezone.utc).isoformat())
        )

def complete_run(run_id: str, result: dict):
    with _conn() as con:
        con.execute(
            "UPDATE runs SET status=?, result=? WHERE run_id=?",
            ("completed", json.dumps(result), run_id)
        )

def get_run(run_id: str) -> Optional[dict]:
    with _conn() as con:
        row = con.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        return dict(row) if row else None

def get_run_events(run_id: str) -> list:
    with _conn() as con:
        rows = con.execute("SELECT event FROM run_events WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
        return [json.loads(r["event"]) for r in rows]
