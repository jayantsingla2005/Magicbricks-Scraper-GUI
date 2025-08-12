#!/usr/bin/env python3
"""
Incremental Database Schema Enhancement
Add tables and columns needed for evidence-based incremental scraping.
Based on comprehensive research findings.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class IncrementalDatabaseSchema:
    """
    Enhanced database schema for incremental scraping functionality
    """
    
    def __init__(self, db_path: str = 'magicbricks_enhanced.db'):
        """Initialize incremental database schema"""
        
        self.db_path = db_path
        self.connection = None
        
        print("[DATABASE] Incremental Database Schema Enhancement Initialized")
    
    def connect(self):
        """Connect to database"""
        
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.execute('PRAGMA foreign_keys = ON')
            print(f"[SUCCESS] Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Database connection failed: {str(e)}")
            return False
    
    def create_incremental_tables(self):
        """Create tables needed for incremental scraping"""
        
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            # 1. Scrape Sessions Table - Track when scrapes happened
            print("📋 Creating scrape_sessions table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scrape_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_timestamp DATETIME NOT NULL,
                    end_timestamp DATETIME,
                    scrape_mode TEXT NOT NULL DEFAULT 'full',
                    city TEXT NOT NULL,
                    pages_scraped INTEGER DEFAULT 0,
                    properties_found INTEGER DEFAULT 0,
                    properties_saved INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'running',
                    stop_reason TEXT,
                    configuration TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. Property URLs Seen Table - Track all URLs we've encountered
            print("📋 Creating property_urls_seen table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS property_urls_seen (
                    url_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_url TEXT UNIQUE NOT NULL,
                    first_seen_date DATETIME NOT NULL,
                    last_seen_date DATETIME NOT NULL,
                    seen_count INTEGER DEFAULT 1,
                    property_id TEXT,
                    title TEXT,
                    city TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 3. Property Posting Dates Table - Track when properties were posted
            print("📋 Creating property_posting_dates table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS property_posting_dates (
                    posting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    property_url TEXT NOT NULL,
                    posting_date_text TEXT NOT NULL,
                    parsed_posting_date DATETIME,
                    extraction_date DATETIME NOT NULL,
                    confidence_score REAL DEFAULT 1.0,
                    parsing_method TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (property_url) REFERENCES property_urls_seen(property_url)
                )
            ''')
            
            # 4. Incremental Settings Table - User preferences and thresholds
            print("📋 Creating incremental_settings table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS incremental_settings (
                    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_name TEXT UNIQUE NOT NULL,
                    setting_value TEXT NOT NULL,
                    setting_type TEXT DEFAULT 'string',
                    description TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 5. Scrape Statistics Table - Performance tracking
            print("📋 Creating scrape_statistics table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scrape_statistics (
                    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    page_number INTEGER NOT NULL,
                    properties_on_page INTEGER DEFAULT 0,
                    new_properties INTEGER DEFAULT 0,
                    seen_properties INTEGER DEFAULT 0,
                    oldest_property_date DATETIME,
                    newest_property_date DATETIME,
                    processing_time_seconds REAL,
                    stop_decision TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES scrape_sessions(session_id)
                )
            ''')
            
            self.connection.commit()
            print("[SUCCESS] All incremental tables created successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error creating incremental tables: {str(e)}")
            self.connection.rollback()
            return False
    
    def add_incremental_columns_to_existing_tables(self):
        """Add incremental tracking columns to existing tables"""
        
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            # Add columns to properties table if they don't exist
            print("📋 Adding incremental columns to properties table...")
            
            # Check existing columns
            cursor.execute("PRAGMA table_info(properties)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            
            columns_to_add = [
                ('first_seen_date', 'DATETIME'),
                ('last_seen_date', 'DATETIME'),
                ('posting_date_text', 'TEXT'),
                ('parsed_posting_date', 'DATETIME'),
                ('scrape_session_id', 'INTEGER'),
                ('is_incremental_new', 'BOOLEAN DEFAULT 0')
            ]
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        cursor.execute(f'ALTER TABLE properties ADD COLUMN {column_name} {column_type}')
                        print(f"   [SUCCESS] Added column: {column_name}")
                    except Exception as e:
                        print(f"   ⚠️ Column {column_name} might already exist: {str(e)}")
            
            self.connection.commit()
            print("[SUCCESS] Incremental columns added to existing tables")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error adding incremental columns: {str(e)}")
            self.connection.rollback()
            return False
    
    def create_indexes_for_performance(self):
        """Create indexes for optimal incremental scraping performance"""
        
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            print("📋 Creating performance indexes...")
            
            # Indexes for fast URL lookups
            indexes = [
                ('idx_property_urls_url', 'property_urls_seen', 'property_url'),
                ('idx_property_urls_first_seen', 'property_urls_seen', 'first_seen_date'),
                ('idx_property_urls_city', 'property_urls_seen', 'city'),
                
                # Indexes for date-based queries
                ('idx_posting_dates_parsed', 'property_posting_dates', 'parsed_posting_date'),
                ('idx_posting_dates_url', 'property_posting_dates', 'property_url'),
                
                # Indexes for session tracking
                ('idx_sessions_start_time', 'scrape_sessions', 'start_timestamp'),
                ('idx_sessions_city_mode', 'scrape_sessions', 'city, scrape_mode'),
                
                # Indexes for statistics
                ('idx_stats_session', 'scrape_statistics', 'session_id'),
                ('idx_stats_page', 'scrape_statistics', 'page_number'),
                
                # Indexes for properties table
                ('idx_properties_first_seen', 'properties', 'first_seen_date'),
                ('idx_properties_posting_date', 'properties', 'parsed_posting_date'),
                ('idx_properties_session', 'properties', 'scrape_session_id')
            ]
            
            for index_name, table_name, columns in indexes:
                try:
                    cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})')
                    print(f"   [SUCCESS] Created index: {index_name}")
                except Exception as e:
                    print(f"   ⚠️ Index {index_name} might already exist: {str(e)}")
            
            self.connection.commit()
            print("[SUCCESS] Performance indexes created successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error creating indexes: {str(e)}")
            self.connection.rollback()
            return False
    
    def insert_default_settings(self):
        """Insert default incremental scraping settings"""
        
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            print("📋 Inserting default incremental settings...")
            
            default_settings = [
                ('incremental_mode', 'date_based', 'string', 'Primary incremental scraping mode'),
                ('stop_threshold_percentage', '80', 'integer', 'Percentage of old properties to trigger stop'),
                ('conservative_mode', 'false', 'boolean', 'Use conservative stopping thresholds'),
                ('max_pages_incremental', '100', 'integer', 'Maximum pages to check in incremental mode'),
                ('date_buffer_hours', '2', 'integer', 'Buffer hours for date-based filtering'),
                ('url_tracking_enabled', 'true', 'boolean', 'Enable URL tracking for validation'),
                ('force_chronological_sort', 'true', 'boolean', 'Force sort=date_desc parameter'),
                ('backup_validation_enabled', 'true', 'boolean', 'Enable multiple validation methods'),
                ('last_full_scrape_date', '', 'datetime', 'Date of last full scrape'),
                ('incremental_scraping_enabled', 'true', 'boolean', 'Master switch for incremental scraping')
            ]
            
            for setting_name, setting_value, setting_type, description in default_settings:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO incremental_settings 
                        (setting_name, setting_value, setting_type, description)
                        VALUES (?, ?, ?, ?)
                    ''', (setting_name, setting_value, setting_type, description))
                    print(f"   [SUCCESS] Added setting: {setting_name} = {setting_value}")
                except Exception as e:
                    print(f"   ⚠️ Setting {setting_name} might already exist: {str(e)}")
            
            self.connection.commit()
            print("[SUCCESS] Default settings inserted successfully")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error inserting default settings: {str(e)}")
            self.connection.rollback()
            return False
    
    def validate_schema_enhancement(self):
        """Validate that all incremental schema enhancements are working"""
        
        if not self.connection:
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            print("🔍 Validating incremental schema enhancement...")
            
            # Check all tables exist
            tables_to_check = [
                'scrape_sessions',
                'property_urls_seen', 
                'property_posting_dates',
                'incremental_settings',
                'scrape_statistics'
            ]
            
            for table in tables_to_check:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if cursor.fetchone():
                    print(f"   [SUCCESS] Table exists: {table}")
                else:
                    print(f"   [ERROR] Table missing: {table}")
                    return False
            
            # Check settings are inserted
            cursor.execute("SELECT COUNT(*) FROM incremental_settings")
            settings_count = cursor.fetchone()[0]
            print(f"   [SUCCESS] Settings configured: {settings_count}")
            
            # Check indexes exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
            indexes = cursor.fetchall()
            print(f"   [SUCCESS] Performance indexes: {len(indexes)}")
            
            print("[SUCCESS] Schema enhancement validation successful")
            return True
            
        except Exception as e:
            print(f"[ERROR] Schema validation failed: {str(e)}")
            return False
    
    def close(self):
        """Close database connection"""
        
        if self.connection:
            self.connection.close()
            print("[SUCCESS] Database connection closed")
    
    def enhance_database_schema(self):
        """Complete database schema enhancement process"""
        
        print("[ROCKET] STARTING DATABASE SCHEMA ENHANCEMENT")
        print("="*60)
        
        try:
            # Step 1: Connect to database
            if not self.connect():
                return False
            
            # Step 2: Create incremental tables
            if not self.create_incremental_tables():
                return False
            
            # Step 3: Add columns to existing tables
            if not self.add_incremental_columns_to_existing_tables():
                return False
            
            # Step 4: Create performance indexes
            if not self.create_indexes_for_performance():
                return False
            
            # Step 5: Insert default settings
            if not self.insert_default_settings():
                return False
            
            # Step 6: Validate everything
            if not self.validate_schema_enhancement():
                return False
            
            print("\n🎉 DATABASE SCHEMA ENHANCEMENT COMPLETE!")
            print("="*60)
            print("[SUCCESS] All incremental tables created")
            print("[SUCCESS] Performance indexes added")
            print("[SUCCESS] Default settings configured")
            print("[SUCCESS] Schema validation passed")
            print("[ROCKET] Ready for incremental scraping implementation")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Database schema enhancement failed: {str(e)}")
            return False
        
        finally:
            self.close()


def main():
    """Main function for database schema enhancement"""
    
    try:
        schema_enhancer = IncrementalDatabaseSchema()
        success = schema_enhancer.enhance_database_schema()
        
        if success:
            print("\n[SUCCESS] Database schema enhancement completed successfully!")
            return True
        else:
            print("\n[ERROR] Database schema enhancement failed!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Schema enhancement error: {str(e)}")
        return False


if __name__ == "__main__":
    main()
