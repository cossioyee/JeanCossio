import sqlite3
import os


def get_connection() -> sqlite3.Connection:
    db_path = os.getenv("DB_PATH", "app.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL,
            email TEXT    NOT NULL UNIQUE
        )
        """
    )
    conn.commit()


def main() -> None:
    with get_connection() as conn:
        init_db(conn)

        conn.execute(
            "INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)",
            ("Jean", "jean@example.com"),
        )
        conn.commit()

        rows = conn.execute("SELECT id, name, email FROM users").fetchall()
        for row in rows:
            print(dict(row))


if __name__ == "__main__":
    main()
