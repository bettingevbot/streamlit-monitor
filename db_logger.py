import psycopg2
from datetime import datetime

DATABASE_CONFIG = {
    "dbname": "horse_aus",
    "user": "postgres",
    "password": "postgres",
    "host": "192.168.1.154",  # Updated from localhost
    "port": "5432"
}

# Define allowed info lines
ALLOWED_INFO_LINES = {105, 113, 131, 140, 988, 79, 995, 996, 978}

class DatabaseLogger:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(**DATABASE_CONFIG)
        except Exception as e:
            print(f"Database connection error: {e}")

    def log_message(self, timestamp, log_level, line_number, message):
        """Log a message to the database if it meets the criteria"""
        if log_level == 'INFO' and int(line_number) in ALLOWED_INFO_LINES:
            try:
                if not self.conn or self.conn.closed:
                    self.connect()
                
                with self.conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO logs_horse_aus 
                        (timestamp, log_level, line_number, message) 
                        VALUES (%s, %s, %s, %s)
                        """,
                        (timestamp, log_level, line_number, message)
                    )
                self.conn.commit()
            except Exception as e:
                print(f"Error writing to database: {e}")

    def close(self):
        if self.conn:
            self.conn.close()

# Usage example:
if __name__ == "__main__":
    # Create the table if it doesn't exist
    conn = psycopg2.connect(**DATABASE_CONFIG)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS logs_horse_aus (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                log_level VARCHAR(10),
                line_number INTEGER,
                message TEXT
            )
        """)
    conn.commit()
    conn.close()

    # Example of how to use the logger
    logger = DatabaseLogger()
    logger.log_message(
        timestamp=datetime.now(),
        log_level='INFO',
        line_number=105,
        message='Test message'
    )
    logger.close()
