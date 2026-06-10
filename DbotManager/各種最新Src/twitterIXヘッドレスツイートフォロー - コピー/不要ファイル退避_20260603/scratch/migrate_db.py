import json
import psycopg2
from loguru import logger

def migrate():
    try:
        with open('db_config.json', 'r', encoding='utf-8') as f:
            conf = json.load(f)['postgres']
        
        conn = psycopg2.connect(conf['uri'])
        cursor = conn.cursor()
        
        logger.info("Checking for missing columns in 'accounts' table...")
        
        columns_to_add = {
            'assigned_pc': 'TEXT',
            'in_use': 'INTEGER DEFAULT 0',
            'claimed_by': 'TEXT',
            'claimed_at': 'TIMESTAMP'
        }
        
        for col, col_type in columns_to_add.items():
            try:
                cursor.execute(f"ALTER TABLE accounts ADD COLUMN {col} {col_type}")
                logger.success(f"Added column: {col}")
            except Exception as e:
                if 'already exists' in str(e):
                    logger.info(f"Column already exists: {col}")
                else:
                    logger.error(f"Failed to add column {col}: {e}")
            conn.commit()

        # Ensure system_commands table exists
        logger.info("Ensuring system_commands table exists...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_commands (
            id SERIAL PRIMARY KEY,
            command TEXT,
            params TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        logger.success("system_commands table verified.")
        conn.commit()
        
        conn.close()
        logger.info("Migration complete.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
