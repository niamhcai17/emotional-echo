#!/usr/bin/env python3
"""
Migration script to add language field to existing database.
Run this script to update your existing database schema.
"""

import sqlite3
import os

def migrate_database():
    """Add language column to phrases table if it doesn't exist"""
    
    # Path to the database file
    db_path = os.path.join('instance', 'entrelineas.db')
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the application first to create the database.")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if language column already exists
        cursor.execute("PRAGMA table_info(phrase)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'language' not in columns:
            # Add language column with default value 'es'
            cursor.execute("ALTER TABLE phrase ADD COLUMN language VARCHAR(2) DEFAULT 'es'")
            conn.commit()
            print("✅ Successfully added 'language' column to database.")
        else:
            print("ℹ️  'language' column already exists in database.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...")
    migrate_database()
    print("✅ Migration completed!") 