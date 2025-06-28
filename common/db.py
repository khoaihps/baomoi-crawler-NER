import sqlite3
from common import config


class SQLiteHook:
    def __init__(self, db_path: str = config.DEFAULT_CACHE_DB) -> None:
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self) -> None:
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS visited_urls (
                    url TEXT PRIMARY KEY
                )
            """)

    def has_visited(self, url: str) -> bool:
        cursor = self.conn.execute("SELECT 1 FROM visited_urls WHERE url = ?", (url,))
        return cursor.fetchone() is not None

    def mark_visited(self, url: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO visited_urls (url) VALUES (?)", (url,)
            )

    def close(self) -> None:
        self.conn.close()
