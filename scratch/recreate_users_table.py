import sqlite3

def fix_users_table():
    conn = sqlite3.connect("nagarik_saarathi.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys=OFF;")
    cursor.execute("BEGIN TRANSACTION;")

    # Create new table with updated check constraint
    cursor.execute("""
    CREATE TABLE users_new (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        identifier VARCHAR(120) NOT NULL,
        email VARCHAR(120),
        mobile VARCHAR(20),
        hashed_password VARCHAR(255) NOT NULL,
        role VARCHAR(20) NOT NULL,
        full_name VARCHAR(120),
        department VARCHAR(150),
        state_scope VARCHAR(10),
        designation VARCHAR(120),
        assigned_by_id INTEGER,
        preferred_language VARCHAR(10) DEFAULT 'en',
        accessibility_settings JSON DEFAULT '{"fontScale": 1, "highContrast": false}' NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        is_demo BOOLEAN NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL,
        last_login_at DATETIME,
        CONSTRAINT ck_user_role CHECK (role IN ('citizen', 'official', 'admin'))
    );
    """)

    # Copy data from users to users_new
    cursor.execute("""
    INSERT INTO users_new (
        id, identifier, email, mobile, hashed_password, role, full_name, department,
        state_scope, designation, assigned_by_id, preferred_language, accessibility_settings,
        is_active, is_demo, created_at, last_login_at
    )
    SELECT
        id, identifier, email, mobile, hashed_password, role, full_name, department,
        state_scope, designation, assigned_by_id, preferred_language, accessibility_settings,
        is_active, is_demo, created_at, last_login_at
    FROM users;
    """)

    cursor.execute("DROP TABLE users;")
    cursor.execute("ALTER TABLE users_new RENAME TO users;")

    # Recreate indices
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_identifier ON users (identifier);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_role ON users (role);")

    conn.commit()
    cursor.execute("PRAGMA foreign_keys=ON;")
    print("users table recreated successfully with ('citizen', 'official', 'admin') check constraint!")

if __name__ == "__main__":
    fix_users_table()
