#!/usr/bin/env python3
"""
Database Manager for MagicBricks Scraper
Provides database integration foundation for large-scale operations.
"""

import sqlite3
import json
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import logging

try:
    from ..models.property_model import PropertyModel
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from models.property_model import PropertyModel


class DatabaseManager:
    """
    Database manager for storing and retrieving property data
    Supports SQLite for local operations and provides foundation for PostgreSQL/MySQL
    """
    
    def __init__(self, db_path: str = "data/magicbricks.db", db_type: str = "sqlite"):
        """Initialize database manager"""
        self.db_path = Path(db_path)
        self.db_type = db_type
        self.connection = None
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with required tables"""
        if self.db_type == "sqlite":
            self._initialize_sqlite()
        else:
            raise ValueError(f"Database type '{self.db_type}' not supported yet")
    
    def _initialize_sqlite(self):
        """Initialize SQLite database"""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Create tables
            self._create_tables()
            
            self.logger.info(f"✅ SQLite database initialized: {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize SQLite database: {str(e)}")
            raise
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self.connection.cursor()
        
        # Properties table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price TEXT,
                price_per_sqft TEXT,
                super_area TEXT,
                carpet_area TEXT,
                bedrooms TEXT,
                bathrooms TEXT,
                balconies TEXT,
                floor TEXT,
                total_floors TEXT,
                age TEXT,
                facing TEXT,
                furnishing TEXT,
                parking TEXT,
                status TEXT,
                possession TEXT,
                society TEXT,
                locality TEXT,
                city TEXT,
                builder TEXT,
                project_name TEXT,
                description TEXT,
                amenities TEXT,
                
                -- Metadata
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_url TEXT,
                page_number INTEGER,
                position_on_page INTEGER,
                
                -- Data quality
                is_valid BOOLEAN DEFAULT 1,
                validation_errors TEXT,
                
                -- Indexing
                UNIQUE(title, price, locality) ON CONFLICT REPLACE
            )
        """)
        
        # Scraping sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                status TEXT NOT NULL,
                total_pages INTEGER DEFAULT 0,
                total_properties INTEGER DEFAULT 0,
                valid_properties INTEGER DEFAULT 0,
                errors INTEGER DEFAULT 0,
                config TEXT,
                performance_stats TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_scraped_at ON properties(scraped_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_locality ON properties(locality)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON scraping_sessions(start_time)")
        
        self.connection.commit()
        self.logger.info("✅ Database tables created successfully")
    
    def store_properties(self, properties: List[PropertyModel], session_id: str, 
                        page_number: int = 1, source_url: str = "") -> int:
        """Store properties in database"""
        if not properties:
            return 0
        
        cursor = self.connection.cursor()
        stored_count = 0
        
        for i, prop in enumerate(properties):
            try:
                # Convert property to database format
                prop_data = self._property_to_db_format(prop, session_id, page_number, i + 1, source_url)
                
                # Insert property
                placeholders = ', '.join(['?' for _ in prop_data.keys()])
                columns = ', '.join(prop_data.keys())
                
                cursor.execute(f"""
                    INSERT OR REPLACE INTO properties ({columns})
                    VALUES ({placeholders})
                """, list(prop_data.values()))
                
                stored_count += 1
                
            except Exception as e:
                self.logger.error(f"❌ Failed to store property {i+1}: {str(e)}")
                continue
        
        self.connection.commit()
        self.logger.info(f"✅ Stored {stored_count}/{len(properties)} properties in database")
        
        return stored_count
    
    def _property_to_db_format(self, prop: PropertyModel, session_id: str, 
                              page_number: int, position: int, source_url: str) -> Dict[str, Any]:
        """Convert PropertyModel to database format"""
        return {
            'title': prop.title,
            'price': prop.price,
            'price_per_sqft': prop.price_per_sqft,
            'super_area': prop.super_area,
            'carpet_area': prop.carpet_area,
            'bedrooms': prop.bedrooms,
            'bathrooms': prop.bathrooms,
            'balconies': prop.balconies,
            'floor': prop.floor,
            'total_floors': prop.total_floors,
            'age': prop.age,
            'facing': prop.facing,
            'furnishing': prop.furnishing,
            'parking': prop.parking,
            'status': prop.status,
            'possession': prop.possession,
            'society': prop.society,
            'locality': prop.locality,
            'city': prop.city,
            'builder': prop.builder,
            'project_name': prop.project_name,
            'description': prop.description,
            'amenities': json.dumps(prop.amenities) if prop.amenities else None,
            'source_url': source_url,
            'page_number': page_number,
            'position_on_page': position,
            'is_valid': prop.is_valid(),
            'validation_errors': json.dumps(prop.get_validation_errors()) if hasattr(prop, 'get_validation_errors') else None
        }
    
    def create_session(self, session_id: str, config: Dict[str, Any]) -> bool:
        """Create a new scraping session"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO scraping_sessions (session_id, start_time, status, config)
                VALUES (?, ?, ?, ?)
            """, (session_id, datetime.now(), 'RUNNING', json.dumps(config)))
            
            self.connection.commit()
            self.logger.info(f"✅ Created scraping session: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create session {session_id}: {str(e)}")
            return False
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update scraping session"""
        try:
            cursor = self.connection.cursor()
            
            # Build update query
            updates = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['end_time', 'status', 'total_pages', 'total_properties', 
                          'valid_properties', 'errors', 'performance_stats']:
                    updates.append(f"{key} = ?")
                    if key == 'performance_stats' and isinstance(value, dict):
                        values.append(json.dumps(value))
                    else:
                        values.append(value)
            
            if updates:
                values.append(session_id)
                cursor.execute(f"""
                    UPDATE scraping_sessions 
                    SET {', '.join(updates)}
                    WHERE session_id = ?
                """, values)
                
                self.connection.commit()
                self.logger.info(f"✅ Updated session: {session_id}")
                return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update session {session_id}: {str(e)}")
            return False
    
    def get_properties(self, limit: Optional[int] = None, 
                      filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Retrieve properties from database"""
        try:
            cursor = self.connection.cursor()
            
            # Build query
            query = "SELECT * FROM properties"
            params = []
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    if key in ['locality', 'city', 'status']:
                        conditions.append(f"{key} = ?")
                        params.append(value)
                    elif key == 'min_price' and value:
                        conditions.append("CAST(REPLACE(REPLACE(price, '₹', ''), ' Cr', '') AS REAL) >= ?")
                        params.append(float(value))
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY scraped_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            properties = [dict(row) for row in rows]
            
            self.logger.info(f"✅ Retrieved {len(properties)} properties from database")
            return properties
            
        except Exception as e:
            self.logger.error(f"❌ Failed to retrieve properties: {str(e)}")
            return []
    
    def export_to_csv(self, output_path: str, filters: Optional[Dict[str, Any]] = None) -> bool:
        """Export properties to CSV"""
        try:
            properties = self.get_properties(filters=filters)
            
            if not properties:
                self.logger.warning("⚠️ No properties to export")
                return False
            
            # Convert to DataFrame and export
            df = pd.DataFrame(properties)
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            self.logger.info(f"✅ Exported {len(properties)} properties to CSV: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export to CSV: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Properties statistics
            cursor.execute("SELECT COUNT(*) FROM properties")
            total_properties = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM properties WHERE is_valid = 1")
            valid_properties = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT locality) FROM properties")
            unique_localities = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT city) FROM properties")
            unique_cities = cursor.fetchone()[0]
            
            # Sessions statistics
            cursor.execute("SELECT COUNT(*) FROM scraping_sessions")
            total_sessions = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM scraping_sessions WHERE status = 'COMPLETED'")
            completed_sessions = cursor.fetchone()[0]
            
            # Recent activity
            cursor.execute("SELECT MAX(scraped_at) FROM properties")
            last_scraped = cursor.fetchone()[0]
            
            return {
                'total_properties': total_properties,
                'valid_properties': valid_properties,
                'unique_localities': unique_localities,
                'unique_cities': unique_cities,
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'last_scraped': last_scraped,
                'database_path': str(self.db_path),
                'database_size_mb': self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get statistics: {str(e)}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("✅ Database connection closed")


# Export for easy import
__all__ = ['DatabaseManager']
