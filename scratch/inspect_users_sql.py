import sqlite3

conn = sqlite3.connect("nagarik_saarathi.db")
sql = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'").fetchone()[0]
print("Current schema:\n", sql)
