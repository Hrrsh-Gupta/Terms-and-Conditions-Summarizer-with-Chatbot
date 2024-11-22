import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMainWindow, QTableWidget, QVBoxLayout, QWidget
import sqlite3

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class Database:
    def __init__(self, db_name="main/summarizer_app.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS LOG (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                time TEXT,
                name TEXT,
                summary_generated BOOLEAN DEFAULT 0
            )
        """)
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

    def get_log_entries(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM LOG ORDER BY session_id DESC")
        return cursor.fetchall()

    def get_session_summaries(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Sessions WHERE session_id = ?", (session_id,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Database Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        layout = QVBoxLayout()

        # Log table
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(5)
        self.log_table.setHorizontalHeaderLabels(["Session ID", "Date", "Time", "Name", "Summary Generated"])
        self.log_table.itemSelectionChanged.connect(self.load_sessions)
        layout.addWidget(self.log_table)

        # Sessions table
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels(["ID", "Session ID", "Time", "Summary Type", "Input", "Summary"])
        layout.addWidget(self.sessions_table)

        # Set the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Load log data
        self.load_log()

    def load_log(self):
        entries = self.db.get_log_entries()
        self.log_table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            for column, data in enumerate(entry):
                self.log_table.setItem(row, column, QTableWidgetItem(str(data)))

    def load_sessions(self):
        selected_items = self.log_table.selectedItems()
        if not selected_items:
            return
        session_id = int(selected_items[0].text())

        sessions = self.db.get_session_summaries(session_id)
        self.sessions_table.setRowCount(len(sessions))
        for row, session in enumerate(sessions):
            for column, data in enumerate(session):
                self.sessions_table.setItem(row, column, QTableWidgetItem(str(data)))

    def closeEvent(self, event):
        self.db.close()
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
