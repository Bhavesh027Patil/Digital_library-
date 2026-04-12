import sqlite3, os

DB_PATH = os.environ.get('DB_PATH', 'database.db')
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')

c.execute('''
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT NOT NULL,
    description TEXT DEFAULT '',
    file_path TEXT NOT NULL,
    file_type TEXT DEFAULT 'raw',
    original_filename TEXT DEFAULT '',
    uploaded_by TEXT DEFAULT 'anonymous',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

# Safe migrations – add columns if missing
MIGRATIONS = [
    "ALTER TABLE notes ADD COLUMN description TEXT DEFAULT ''",
    "ALTER TABLE notes ADD COLUMN file_type TEXT DEFAULT 'raw'",
    "ALTER TABLE notes ADD COLUMN original_filename TEXT DEFAULT ''",
    "ALTER TABLE notes ADD COLUMN uploaded_by TEXT DEFAULT 'anonymous'",
    "ALTER TABLE notes ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
]
for sql in MIGRATIONS:
    try:
        c.execute(sql)
    except Exception:
        pass

conn.commit()
conn.close()
print("✓ Database ready.")