import sqlite3
from datetime import datetime, timezone
from config import DATABASE_PATH

def connect():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            accused TEXT NOT NULL,
            claimant TEXT NOT NULL,
            judge_id INTEGER NOT NULL,
            hearing_at TEXT,
            hearing_place TEXT,
            charges TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'OTEVRENY',
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS government_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            effective_at TEXT,
            status TEXT NOT NULL DEFAULT 'NAVRH',
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            reference TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)

def now():
    return datetime.now(timezone.utc).isoformat()

def audit(db, actor_id, action, reference):
    db.execute("INSERT INTO audit_log(actor_id,action,reference,created_at) VALUES (?,?,?,?)",
               (actor_id, action, reference, now()))
