import sqlite3

con = sqlite3.connect('nagarik_saarathi.db')
cur = con.cursor()
tables = [row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print('departments in DB:', 'departments' in tables)
print('scheme_proposals in DB:', 'scheme_proposals' in tables)
print('admin_audit_logs in DB:', 'admin_audit_logs' in tables)

user_cols = [c[1] for c in cur.execute("PRAGMA table_info(users)").fetchall()]
print('users columns:', user_cols)
