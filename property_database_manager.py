#!/usr/bin/env python3
"""
Property Database Manager
Handles database connections, schema setup, and database operations for individual property tracking.
"""

import sqlite3
from typing import Optional


class PropertyDatabaseManager:
    """
    Manages database connections and schema for individual property tracking
    """
    
    def __init__(self, db_path: str = 'magicbricks_enhanced.db'):
        """Initialize database manager"""
        self.db_path = db_path
        self.connection = None
    
    def connect_db(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"[ERROR] Database connection failed: {str(e)}")
            return False
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def setup_database_schema(self):
        """Create necessary tables for individual property tracking"""
        
        if not self.connect_db():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # 1. Individual Properties Scraped Tracking Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS individual_properties_scraped (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_url TEXT UNIQUE NOT NULL,
                    property_id TEXT,
                    url_hash TEXT UNIQUE,
                    scraped_at DATETIME NOT NULL,
                    scraping_session_id INTEGER,
                    data_quality_score REAL DEFAULT 0.0,
                    extraction_success BOOLEAN DEFAULT 1,
                    retry_count INTEGER DEFAULT 0,
                    last_retry_at DATETIME,
                    force_rescrape_after DATETIME,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. Detailed Property Data Storage Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS property_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_url TEXT NOT NULL,
                    title TEXT,
                    price TEXT,
                    area TEXT,
                    locality TEXT,
                    society TEXT,
                    property_type TEXT,
                    bhk TEXT,
                    bathrooms TEXT,
                    furnishing TEXT,
                    floor TEXT,
                    age TEXT,
                    facing TEXT,
                    parking TEXT,
                    amenities TEXT,
                    description TEXT,
                    builder_info TEXT,
                    location_details TEXT,
                    specifications TEXT,
                    contact_info TEXT,
                    images TEXT,  -- JSON array
                    raw_html TEXT,
                    scraped_at DATETIME NOT NULL,
                    data_quality_score REAL DEFAULT 0.0,
                    extraction_metadata TEXT,  -- JSON
                    FOREIGN KEY (property_url) REFERENCES individual_properties_scraped(property_url)
                )
            ''')
            
            # 3. Individual Property Scraping Sessions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS individual_scraping_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL,
                    start_timestamp DATETIME NOT NULL,
                    end_timestamp DATETIME,
                    total_urls_requested INTEGER DEFAULT 0,
                    new_properties_scraped INTEGER DEFAULT 0,
                    duplicates_skipped INTEGER DEFAULT 0,
                    failed_scraping INTEGER DEFAULT 0,
                    average_quality_score REAL DEFAULT 0.0,
                    session_config TEXT,  -- JSON
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 4. Property Change History (for tracking price/status changes)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS property_change_history (
                    change_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_url TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    change_detected_at DATETIME NOT NULL,
                    scraping_session_id INTEGER,
                    FOREIGN KEY (property_url) REFERENCES individual_properties_scraped(property_url)
                )
            ''')
            
            # Create indexes for performance
            indexes = [
                ('idx_individual_scraped_url', 'individual_properties_scraped', 'property_url'),
                ('idx_individual_scraped_hash', 'individual_properties_scraped', 'url_hash'),
                ('idx_individual_scraped_date', 'individual_properties_scraped', 'scraped_at'),
                ('idx_individual_scraped_quality', 'individual_properties_scraped', 'data_quality_score'),
                ('idx_property_details_url', 'property_details', 'property_url'),
                ('idx_property_details_scraped', 'property_details', 'scraped_at'),
                ('idx_individual_sessions_start', 'individual_scraping_sessions', 'start_timestamp'),
                ('idx_change_history_url', 'property_change_history', 'property_url'),
                ('idx_change_history_date', 'property_change_history', 'change_detected_at')
            ]
            
            for index_name, table_name, column_name in indexes:
                try:
                    cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name})')
                except Exception as e:
                    print(f"[WARNING] Could not create index {index_name}: {str(e)}")
            
            self.connection.commit()
            print("[SUCCESS] Individual property tracking database schema created")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to create database schema: {str(e)}")
            return False
        
        finally:
            self.close_connection()
    
    def get_connection(self) -> Optional[sqlite3.Connection]:
        """Get current database connection"""
        return self.connection

