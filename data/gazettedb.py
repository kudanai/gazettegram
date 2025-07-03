import sqlite3
import json
from api.gazette_types import Iulaan


class GazetteDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS iulaan (
                id TEXT PRIMARY KEY,
                title TEXT,
                office_name TEXT,
                iulaan_type TEXT,
                additional_info TEXT, -- Stored as JSON
                attachments TEXT,     -- Stored as JSON
                body TEXT,
                is_processed BOOLEAN DEFAULT FALSE
            )
        """
        )

        conn.commit()
        conn.close()

    def insert_iulaan(self, iulaan: Iulaan):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO iulaan (id, title, office_name, iulaan_type, additional_info, attachments, body, is_processed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            iulaan.id,
            iulaan.title,
            iulaan.office_name,
            iulaan.iulaan_type,
            json.dumps(iulaan.additional_info, ensure_ascii=False),
            json.dumps(iulaan.attachments, ensure_ascii=False),
            iulaan.body,
            False  # A new or replaced iulaan is not yet processed
        ))
        conn.commit()
        conn.close()

    def get_iulaan(self, iulaan_id: str) -> Iulaan | None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, office_name, iulaan_type, additional_info, attachments, body FROM iulaan WHERE id = ?", (iulaan_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Iulaan(
                id=row[0],
                title=row[1],
                office_name=row[2],
                iulaan_type=row[3],
                additional_info=json.loads(row[4]),
                attachments=json.loads(row[5]),
                body=row[6]
            )
        return None

    def iulaan_exists(self, iulaan_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM iulaan WHERE id = ?", (iulaan_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def get_all_iulaan(self, is_processed: bool | None = None) -> list[Iulaan]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT id, title, office_name, iulaan_type, additional_info, attachments, body FROM iulaan"
        params = []
        if is_processed is not None:
            query += " WHERE is_processed = ?"
            params.append(is_processed)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()

        iulaans = []
        for row in rows:
            iulaans.append(Iulaan(
                id=row[0],
                title=row[1],
                office_name=row[2],
                iulaan_type=row[3],
                additional_info=json.loads(row[4]),
                attachments=json.loads(row[5]),
                body=row[6]
            ))
        return iulaans

    def set_iulaan_processed(self, iulaan_id: str, status: bool = True):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE iulaan SET is_processed = ? WHERE id = ?", (status, iulaan_id))
        conn.commit()
        conn.close()
