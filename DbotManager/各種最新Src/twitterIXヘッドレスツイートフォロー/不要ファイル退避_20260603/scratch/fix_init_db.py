    def init_db(self):
        try:
            logger.info("Initializing database...")
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.db_type in ["mysql", "postgres"]:
                logger.debug(f"Ensuring tables exist in {self.db_type}...")
                text_type = "VARCHAR(255)" if self.db_type == 'mysql' else "TEXT"
                time_type = "DATETIME" if self.db_type == 'mysql' else "TIMESTAMP"
                
                # Accounts Table
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS accounts (
                    id SERIAL PRIMARY KEY,
                    username {text_type} UNIQUE,
                    screen_name {text_type},
                    password {text_type},
                    email {text_type},
                    auth_token {text_type},
                    ct0 {text_type},
                    totp_secret {text_type},
                    is_suspended BOOLEAN DEFAULT FALSE,
                    status_message TEXT,
                    sync_status TEXT DEFAULT '',
                    "Select" BOOLEAN DEFAULT TRUE,
                    is_alive BOOLEAN DEFAULT TRUE,
                    category TEXT DEFAULT '日常生活',
                    last_active_date TEXT,
                    display_name TEXT,
                    name TEXT,
                    biography TEXT,
                    last_tweet_at {time_type},
                    last_full_check {time_type},
                    claimed_by TEXT,
                    claimed_at {time_type},
                    assigned_pc TEXT,
                    in_use INTEGER DEFAULT 0,
                    following_count INTEGER DEFAULT 0,
                    followers_count INTEGER DEFAULT 0,
                    reach_status TEXT DEFAULT 'OK'
                )
                ''')
                # インデックスの作成
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_screen_name ON accounts (screen_name)")
                logger.debug("Accounts table verified with index.")
                
                # Relationships Table
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS relationships (
                    from_user {text_type},
                    to_user {text_type},
                    timestamp {time_type} DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (from_user, to_user)
                )
                ''')
                # Daily Stats
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    username {text_type},
                    date DATE,
                    action_type {text_type},
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (username, date, action_type)
                )
                ''')
                
                # System Commands Table
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS system_commands (
                    id SERIAL PRIMARY KEY,
                    command {text_type},
                    params TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                if self.db_type != "mysql": conn.commit()
                logger.debug(f"{self.db_type} tables verified.")
            else:
                # SQLite (Local Fallback)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    screen_name TEXT,
                    password TEXT,
                    email TEXT,
                    auth_token TEXT,
                    ct0 TEXT,
                    totp_secret TEXT,
                    is_suspended INTEGER DEFAULT 0,
                    status_message TEXT,
                    sync_status TEXT DEFAULT '',
                    "Select" INTEGER DEFAULT 1,
                    is_alive INTEGER DEFAULT 1,
                    category TEXT DEFAULT '日常生活',
                    last_active_date TEXT,
                    display_name TEXT,
                    name TEXT,
                    biography TEXT,
                    last_tweet_at TEXT,
                    last_full_check TEXT,
                    claimed_by TEXT,
                    claimed_at TEXT,
                    assigned_pc TEXT,
                    in_use INTEGER DEFAULT 0,
                    following_count INTEGER DEFAULT 0,
                    followers_count INTEGER DEFAULT 0,
                    reach_status TEXT DEFAULT 'OK'
                )
                ''')
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_screen_name ON accounts (screen_name)")
                
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    username TEXT,
                    date TEXT,
                    action_type TEXT,
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (username, date, action_type)
                )
                ''')
                
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT,
                    params TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                conn.commit()
                logger.debug("SQLite tables verified.")

            # Identify PC
            self.identify_pc()
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise e
