import sqlite3
from contextlib import closing

class JobDatabase:
    def __init__(self, db_path='jobs.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    status TEXT,
                    start_time REAL,
                    end_time REAL
                )
                ''')

    def add_job(self, job_id, status, start_time):
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute('''
                INSERT INTO jobs (id, status, start_time)
                VALUES (?, ?, ?)
                ''', (job_id, status, start_time))

    def update_job(self, job_id, status, end_time=None):
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.execute('''
                UPDATE jobs
                SET status = ?, end_time = ?
                WHERE id = ?
                ''', (status, end_time, job_id))

    def get_job(self, job_id):
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT status, start_time, end_time
            FROM jobs
            WHERE id = ?
            ''', (job_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'status': row[0],
                    'start_time': row[1],
                    'end_time': row[2]
                }
            return None
