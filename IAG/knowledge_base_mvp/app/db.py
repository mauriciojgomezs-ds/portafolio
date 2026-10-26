import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "kb.sqlite"

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS sources (
    tag TEXT PRIMARY KEY,
    base_url TEXT NOT NULL,
    include_pattern TEXT DEFAULT '',
    exclude_pattern TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    source_tag TEXT,
    title TEXT,
    domain TEXT,
    first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_checked_at TEXT,
    current_hash TEXT,
    status_code INTEGER,
    content_type TEXT
);

CREATE TABLE IF NOT EXISTS document_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT,
    clean_text TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS document_fts USING fts5(
    title,
    clean_text,
    url UNINDEXED,
    document_id UNINDEXED,
    version_id UNINDEXED
);

CREATE TABLE IF NOT EXISTS validated_qa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS validated_qa_fts USING fts5(
    question,
    answer,
    sources UNINDEXED,
    qa_id UNINDEXED
);

CREATE TABLE IF NOT EXISTS error_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    bad_answer TEXT,
    reason TEXT,
    better_query TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS error_cases_fts USING fts5(
    question,
    bad_answer,
    reason,
    better_query,
    error_id UNINDEXED
);

CREATE TABLE IF NOT EXISTS search_strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    query TEXT NOT NULL,
    worked INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS change_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    old_hash TEXT,
    new_hash TEXT,
    detected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary TEXT,
    FOREIGN KEY(document_id) REFERENCES documents(id)
);
"""


def connect(db_path: Path = DEFAULT_DB) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DEFAULT_DB) -> None:
    with connect(db_path) as conn:
        conn.executescript(SCHEMA)
        # Migraciones livianas para bases creadas por versiones anteriores del MVP.
        cols = [r[1] for r in conn.execute("PRAGMA table_info(documents)").fetchall()]
        if "source_tag" not in cols:
            conn.execute("ALTER TABLE documents ADD COLUMN source_tag TEXT")
