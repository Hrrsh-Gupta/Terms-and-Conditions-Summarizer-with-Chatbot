import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_name="main/summarizer_app.db"):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "summarizer_app.db")
        self.db_name = db_name

        self.conn = sqlite3.connect(DB_PATH)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create or alter LOG table to include summary_generated column
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS LOG (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                time TEXT,
                name TEXT,
                summary_generated BOOLEAN DEFAULT 0  -- Adds the new column with default False
            )
        """)
        
        # Create Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                time TEXT,
                summary_type TEXT,
                input TEXT,
                summary TEXT,
                FOREIGN KEY(session_id) REFERENCES LOG(session_id)
            )
        """)
        
        self.conn.commit()

    def add_log_entry(self, name = "None"):
        cursor = self.conn.cursor()
        date = datetime.now().strftime("%d-%m-%y")  # Format date as DD-MM-YY
        time = datetime.now().strftime("%I:%M:%S %p")  # Format time as 12-hour clock with AM/PM
        cursor.execute("""
            INSERT INTO LOG (date, time, name, summary_generated) 
            VALUES (?, ?, ?, ?)
        """, (date, time, name, False))  # summary_generated defaults to False
        self.conn.commit()
        return cursor.lastrowid  # Return the generated session_id

    def update_summary_generated(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE LOG SET summary_generated = 1 WHERE session_id = ?
        """, (session_id,))
        self.conn.commit()

    def add_session_entry(self, session_id, summary_type, input_text, summary):
        cursor = self.conn.cursor()
        time = datetime.now().strftime("%I:%M:%S %p")  # Format time as 12-hour clock with AM/PM
        cursor.execute("""
            INSERT INTO Sessions (session_id, time, summary_type, input, summary) 
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, time, summary_type, input_text, summary))
        self.conn.commit()
        # Mark summary_generated as True in LOG table for this session
        self.update_summary_generated(session_id)

    def get_log_entries(self,limit = 25):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM LOG WHERE summary_generated = 1 ORDER BY session_id DESC LIMIT ?", (limit,))
        return cursor.fetchall()  # Returns list of tuples (session_id, date, time, name, summary_generated)
    
    def get_log_entry(self,session_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM LOG WHERE session_id = ?", (session_id,))
        return cursor.fetchone()
    
    def update_session_name(self, session_id, new_name):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE LOG SET name = ? WHERE session_id = ?
        """, (new_name, session_id))
        self.conn.commit()

    def get_session_summaries(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Sessions WHERE session_id = ?", (session_id,))
        return cursor.fetchall()  # Returns list of tuples with session details
    
    def get_session_alias(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM LOG WHERE session_id = ?", (session_id,))
        result = cursor.fetchone()
        return result[0]
    
    def reset_summary_generated(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE LOG SET summary_generated = 0 WHERE session_id = ?
        """, (session_id,))
        self.conn.commit()

    def delete_log_entry(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM LOG WHERE session_id = ?", (session_id,))
        self.conn.commit()

    def delete_session_summaries(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM Sessions WHERE session_id = ?", (session_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
