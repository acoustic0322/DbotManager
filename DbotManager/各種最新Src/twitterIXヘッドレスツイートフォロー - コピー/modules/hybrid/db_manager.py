
import sqlite3
import datetime
import os
from loguru import logger
import pandas as pd

DB_PATH = 'data/bot_data_v2.db'

class DBManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()

    def _ensure_db_dir(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _init_db(self):
        """Initializes the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Accounts Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                username TEXT PRIMARY KEY,
                profile_id TEXT,
                email TEXT,
                password TEXT,
                auth_token TEXT,
                ct0 TEXT,
                is_alive BOOLEAN DEFAULT 1,
                profile_updated BOOLEAN DEFAULT 0,
                last_active_at DATETIME,
                daily_follow_count INTEGER DEFAULT 0,
                daily_followed_by_count INTEGER DEFAULT 0,
                last_reset_date DATE
            )
        ''')

        # Relationships Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_user TEXT,
                to_user TEXT,
                status TEXT DEFAULT 'pending', -- pending, done, failed
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(from_user, to_user)
            )
        ''')

        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def import_from_csv(self, csv_path):
        """Imports accounts from CSV to DB, updating existing ones."""
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return

        df = pd.read_csv(csv_path)
        conn = self.get_connection()
        cursor = conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            if pd.isna(row.get('auth_token')):
                continue

            username = row['screen_name']
            # Using INSERT OR REPLACE to update tokens
            cursor.execute('''
                INSERT OR REPLACE INTO accounts (username, password, email, auth_token, ct0, is_alive, profile_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                username, 
                row.get('password'), 
                row.get('email'), 
                row.get('auth_token'), 
                row.get('ct0'),
                1, # Assume alive on import
                1 # Assume updated if in CSV
            ))
            # Note: daily counts will reset if replaced? Yes.
            # To preserve counts, we might need UPSERT logic but sqlite 3.24+ supports ON CONFLICT
            # For simplicity in this speed-run, replacement is acceptable as CSV is master.
            # OR better: use ON CONFLICT DO UPDATE
            
            # Re-doing with safer upsert for counts
            cursor.execute('''
                 INSERT INTO accounts (username, password, email, auth_token, ct0)
                 VALUES (?, ?, ?, ?, ?)
                 ON CONFLICT(username) DO UPDATE SET
                    auth_token=excluded.auth_token,
                    ct0=excluded.ct0,
                    password=excluded.password
            ''', (username, row.get('password'), row.get('email'), row.get('auth_token'), row.get('ct0')))
            
            count += 1
            
        conn.commit()
        conn.close()
        logger.info(f"Imported/Updated {count} accounts from CSV.")

    def check_daily_reset(self):
        """Resets daily counters if date changed."""
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.date.today().isoformat()
        
        # Check one record
        cursor.execute("SELECT last_reset_date FROM accounts LIMIT 1")
        row = cursor.fetchone()
        
        if not row or row[0] != today:
            logger.info("Resetting daily counters...")
            cursor.execute("UPDATE accounts SET daily_follow_count = 0, daily_followed_by_count = 0, last_reset_date = ?", (today,))
            conn.commit()
            
        conn.close()

    def get_next_task(self):
        """
        Selects a pair (from_user, to_user) based on logic:
        - From: daily_follow_count < 2, alive, not active recently (optional)
        - To: daily_followed_by_count < 3, alive
        - Not already followed
        """
        self.check_daily_reset()
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get Candidates for From (Follower)
        # Randomize to distribute load? Order by last_active_at?
        # Speed priority -> Limit 1 is fine if called in loop
        
        query = '''
            SELECT a1.username, a2.username
            FROM accounts a1
            CROSS JOIN accounts a2
            WHERE a1.username != a2.username
            AND a1.is_alive = 1 AND a2.is_alive = 1
            AND a1.daily_follow_count < 2
            AND a2.daily_followed_by_count < 3
            AND NOT EXISTS (
                SELECT 1 FROM relationships r 
                WHERE r.from_user = a1.username AND r.to_user = a2.username AND r.status IN ('done', 'pending')
            )
            ORDER BY RANDOM()
            LIMIT 1
        '''
        
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0], row[1] # from, to
        return None, None

    def get_account(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE username = ?", (username,))
        # Convert to dict
        row = cursor.fetchone()
        conn.close()
        if row:
             # Basic mapping, should improve if column order changes
             # schema: username, profile_id, ... 
             cols = [description[0] for description in cursor.description]
             return dict(zip(cols, row))
        return None

    def mark_success(self, from_user, to_user):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Add relation
        cursor.execute("INSERT INTO relationships (from_user, to_user, status) VALUES (?, ?, 'done')", (from_user, to_user))
        
        # Update counts
        cursor.execute("UPDATE accounts SET daily_follow_count = daily_follow_count + 1, last_active_at = CURRENT_TIMESTAMP WHERE username = ?", (from_user,))
        cursor.execute("UPDATE accounts SET daily_followed_by_count = daily_followed_by_count + 1 WHERE username = ?", (to_user,))
        
        conn.commit()
        conn.close()
    
    def mark_failed(self, from_user, to_user, reason="error"):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO relationships (from_user, to_user, status) VALUES (?, ?, ?)", (from_user, to_user, 'failed_' + reason))
        conn.commit()
        conn.close()

    def mark_frozen(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE accounts SET is_alive = 0 WHERE username = ?", (username,))
        conn.commit()
        conn.close()
