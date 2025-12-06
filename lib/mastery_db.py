import sqlite3 as sql
import contextlib
import os
import uuid

class MasteryDB:
    # TODO: scrub data before running sql commands
    def __init__(self, db_path = ""):
        self.db_path = db_path

        if os.path.exists(self.db_path):
            self.new_db = False
        else:
            self.new_db = True

    @contextlib.contextmanager
    def get_cursor(self):
        """
        A context manager to safely open a connection and yield a cursor.
        """
        conn = sql.connect(self.db_path)
        conn.row_factory = sql.Row

        try:
            cursor = conn.cursor()
            yield cursor
            conn.commit() # Commit automatically if no errors occur within the 'with' block
        except Exception:
            conn.rollback() # Rollback if an error occurs
            raise
        finally:
            conn.close()

    def _make_user_table(self):
        with self.get_cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE
                )
            ''')

    def _make_container_table(self):
        with self.get_cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS containers (
                    id TEXT PRIMARY KEY,
                    xp_level REAL,
                    level TEXT,
                    name TEXT UNIQUE,
                    user_uuid TEXT,
                    FOREIGN KEY (user_uuid) REFERENCES users(id)
                )
            ''')

    def fetch_existing_db_data(self) -> tuple:
        if not self.new_db:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                user_rows = cursor.fetchall()
                user_rows = [dict(row) for row in user_rows]

                cursor.execute("SELECT * FROM containers")
                container_rows = cursor.fetchall()
                container_rows = [dict(row) for row in container_rows]

            if not user_rows:
                return ()
            return user_rows, container_rows
        return ()

    def delete_db(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"{self.db_path} has been deleted.")
        else:
            print(f"{self.db_path} does not exist.")

    def insert_user_db(self, id, username):
        with self.get_cursor() as cursor:
            cursor.execute("INSERT OR IGNORE INTO users (id, username) VALUES (?,?)", (id, username))
    
    def insert_container_db(self, name, user_id):
        with self.get_cursor() as cursor:
            cursor.execute("INSERT OR IGNORE INTO containers (id, xp_level, level, name, user_uuid) VALUES (?,?,?,?,?)", (str(uuid.uuid4()),0, 'Novice', name, user_id))

    def update_container_db(self, id, xp_level, level):
        with self.get_cursor() as cursor:
            cursor.execute("""
                UPDATE containers
                SET xp_level = ?, level = ?
                WHERE id = ?
            """, (xp_level, level, id))

    def update_user_db(self, id, name):
        with self.get_cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET username = ?
                WHERE id = ?
            """, (name, id))
    
    def delete_container_db(self, id):
        with self.get_cursor() as cursor:
            cursor.execute("DELETE FROM containers WHERE id = ?", (id,))

    def setup_mastery_db(self) -> tuple:
        self._make_user_table()
        self._make_container_table()
        if self.new_db:
            return ()
        else:
            return self.fetch_existing_db_data()
