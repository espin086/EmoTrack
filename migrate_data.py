#!/usr/bin/env python3
"""
Script to migrate data from the old emotions.db to the new structure
"""

import sqlite3
import os
import shutil
from datetime import datetime

def migrate_database():
    """Migrate the old emotions.db to the new structure"""
    
    old_db_path = "emotions.db"
    new_db_path = "data/emotions.db"
    
    # Check if old database exists
    if not os.path.exists(old_db_path):
        print("No existing emotions.db found. Nothing to migrate.")
        return
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # If new database already exists, backup it
    if os.path.exists(new_db_path):
        backup_path = f"{new_db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(new_db_path, backup_path)
        print(f"Existing database backed up to: {backup_path}")
    
    # Copy old database to new location
    shutil.copy2(old_db_path, new_db_path)
    print(f"Copied {old_db_path} to {new_db_path}")
    
    # Update the schema if needed
    conn = sqlite3.connect(new_db_path)
    cursor = conn.cursor()
    
    try:
        # Check if we need to add new columns
        cursor.execute("PRAGMA table_info(emotions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "id" not in columns:
            # Create new table with updated schema
            cursor.execute("""
                CREATE TABLE emotions_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    emotion TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copy data from old table
            cursor.execute("""
                INSERT INTO emotions_new (timestamp, emotion)
                SELECT timestamp, emotion FROM emotions
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE emotions")
            cursor.execute("ALTER TABLE emotions_new RENAME TO emotions")
            
            print("Updated database schema")
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM emotions")
        count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT emotion, COUNT(*) as cnt 
            FROM emotions 
            GROUP BY emotion 
            ORDER BY cnt DESC
        """)
        emotion_stats = cursor.fetchall()
        
        conn.commit()
        
        print(f"\nMigration complete!")
        print(f"Total emotions migrated: {count}")
        print("\nEmotion distribution:")
        for emotion, cnt in emotion_stats:
            print(f"  {emotion}: {cnt}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()