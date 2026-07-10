"""
history_manager.py
------------------
Handles reading / writing scan history to a local SQLite database.
Replaces the flat JSON file used in v1.
"""

import json
import os
import sqlite3
from datetime import datetime

_DIR         = os.path.dirname(__file__)
HISTORY_DB   = os.path.join(_DIR, "history.db")
HISTORY_FILE = os.path.join(_DIR, "history.json")   # legacy — migration only


# =============================================================================
# DB SETUP
# =============================================================================
def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(HISTORY_DB)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                name           TEXT,
                path           TEXT,
                timestamp      TEXT,
                overall_risk   TEXT,
                authentic      INTEGER,
                ai_score       REAL,
                deepfake_score REAL,
                sensitive      TEXT
            )
        """)
        conn.commit()


_init_db()

# =============================================================================
# PUBLIC API
# =============================================================================
def add_record(image_path: str, results: dict) -> None:
    """Append one scan result to the database."""
    deepfake       = results.get("deepfake", {})
    ai_score       = deepfake.get("ai_score")
    deepfake_score = deepfake.get("deepfake_score")

    # Strip 'reason' before saving
    sensitive_clean = {}
    for cat, info in results.get("sensitive", {}).items():
        sensitive_clean[cat] = {
            "subcategory": info.get("subcategory", ""),
            "score":       info.get("score", 0.0),
        }

    with _get_conn() as conn:
        conn.execute("""
            INSERT INTO scans
            (name, path, timestamp, overall_risk, authentic,
             ai_score, deepfake_score, sensitive)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            os.path.basename(image_path),
            image_path,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            results.get("overall_risk", "Low"),
            1 if results.get("authentic", True) else 0,
            ai_score,
            deepfake_score,
            json.dumps(sensitive_clean),
        ))
        conn.commit()


def get_all_records() -> list:
    """Return all history records, newest first."""
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM scans ORDER BY id DESC"
        ).fetchall()

    records = []
    for r in rows:
        record = dict(r)
        record["authentic"] = bool(record["authentic"])
        record["sensitive"] = json.loads(record.get("sensitive") or "{}")
        records.append(record)
    return records


def get_stats() -> dict:
    """Aggregate stats for Dashboard cards."""
    with _get_conn() as conn:
        total       = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        ai_detected = conn.execute(
            "SELECT COUNT(*) FROM scans WHERE ai_score >= 50").fetchone()[0]
        sensitive   = conn.execute(
            "SELECT COUNT(*) FROM scans WHERE sensitive != '{}'").fetchone()[0]
        clean       = conn.execute(
            "SELECT COUNT(*) FROM scans WHERE authentic = 1").fetchone()[0]

    return {
        "total":       total,
        "ai_detected": ai_detected,
        "sensitive":   sensitive,
        "clean":       clean,
    }


def clear_history() -> None:
    """Wipe all history."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM scans")
        conn.commit() 