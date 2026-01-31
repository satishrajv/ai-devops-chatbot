"""
State Tracker
Tracks processed files using SQLite to avoid reprocessing
"""

import sqlite3
from typing import Optional
import logging
from pathlib import Path
from config.settings import settings

logger = logging.getLogger(__name__)


class StateTracker:
    """Tracks file processing state in SQLite database"""

    def __init__(self):
        self.db_path = settings.STATE_DB_PATH
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_state (
                    s3_key TEXT PRIMARY KEY,
                    etag TEXT NOT NULL,
                    weaviate_uuid TEXT,
                    last_processed TEXT NOT NULL,
                    processed_count INTEGER DEFAULT 1
                )
            ''')

            conn.commit()
            conn.close()

            logger.debug(f"Database initialized: {self.db_path}")

        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def is_file_changed(self, s3_key: str, current_etag: str) -> bool:
        """
        Check if file has changed since last processing
        Returns True if file is new or ETag has changed
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                'SELECT etag FROM file_state WHERE s3_key = ?',
                (s3_key,)
            )

            result = cursor.fetchone()
            conn.close()

            if result is None:
                # File not seen before
                logger.debug(f"New file detected: {s3_key}")
                return True

            stored_etag = result[0]

            if stored_etag != current_etag:
                # ETag changed - file modified
                logger.debug(f"File changed: {s3_key} (old ETag: {stored_etag}, new ETag: {current_etag})")
                return True

            # File unchanged
            logger.debug(f"File unchanged: {s3_key}")
            return False

        except Exception as e:
            logger.error(f"Error checking file state: {str(e)}")
            # Default to processing the file if we can't check
            return True

    def update_file_state(self, s3_key: str, etag: str, weaviate_uuid: str):
        """
        Update file processing state
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if record exists
            cursor.execute(
                'SELECT processed_count FROM file_state WHERE s3_key = ?',
                (s3_key,)
            )
            result = cursor.fetchone()

            from datetime import datetime
            now = datetime.now().isoformat()

            if result is None:
                # Insert new record
                cursor.execute('''
                    INSERT INTO file_state (s3_key, etag, weaviate_uuid, last_processed, processed_count)
                    VALUES (?, ?, ?, ?, 1)
                ''', (s3_key, etag, weaviate_uuid, now))

                logger.debug(f"Inserted state for: {s3_key}")

            else:
                # Update existing record
                processed_count = result[0] + 1

                cursor.execute('''
                    UPDATE file_state
                    SET etag = ?, weaviate_uuid = ?, last_processed = ?, processed_count = ?
                    WHERE s3_key = ?
                ''', (etag, weaviate_uuid, now, processed_count, s3_key))

                logger.debug(f"Updated state for: {s3_key} (processed {processed_count} times)")

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating file state: {str(e)}")
            raise

    def get_file_state(self, s3_key: str) -> Optional[dict]:
        """Get state for a specific file"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                'SELECT etag, weaviate_uuid, last_processed, processed_count FROM file_state WHERE s3_key = ?',
                (s3_key,)
            )

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    's3_key': s3_key,
                    'etag': result[0],
                    'weaviate_uuid': result[1],
                    'last_processed': result[2],
                    'processed_count': result[3]
                }

            return None

        except Exception as e:
            logger.error(f"Error getting file state: {str(e)}")
            return None

    def get_all_states(self):
        """Get all file states"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT s3_key, etag, weaviate_uuid, last_processed, processed_count FROM file_state')

            results = cursor.fetchall()
            conn.close()

            states = []
            for row in results:
                states.append({
                    's3_key': row[0],
                    'etag': row[1],
                    'weaviate_uuid': row[2],
                    'last_processed': row[3],
                    'processed_count': row[4]
                })

            return states

        except Exception as e:
            logger.error(f"Error getting all states: {str(e)}")
            return []

    def reset_state(self):
        """Clear all state (useful for testing)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM file_state')

            conn.commit()
            conn.close()

            logger.info("State database cleared")

        except Exception as e:
            logger.error(f"Error resetting state: {str(e)}")
            raise
