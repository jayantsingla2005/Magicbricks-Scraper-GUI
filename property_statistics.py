#!/usr/bin/env python3
"""
Property Statistics
Retrieves scraping statistics for individual property tracking.
"""

from typing import Dict, Any, Optional
from property_database_manager import PropertyDatabaseManager


class PropertyStatistics:
    """
    Provides statistics and reporting from the tracking database
    """

    def __init__(self, db_manager: PropertyDatabaseManager):
        self.db_manager = db_manager

    def get_scraping_statistics(self, session_id: int = None) -> Dict[str, Any]:
        """Get comprehensive scraping statistics (overall or per-session)."""

        if not self.db_manager.connect_db():
            return {'success': False, 'error': 'Database connection failed'}

        try:
            cursor = self.db_manager.connection.cursor()

            stats: Dict[str, Any] = {'success': True}

            if session_id:
                # Session-specific stats
                cursor.execute('''
                    SELECT * FROM individual_scraping_sessions
                    WHERE session_id = ?
                ''', (session_id,))
                session_data = cursor.fetchone()
                if session_data:
                    stats['session'] = dict(session_data)

            # Overall statistics
            cursor.execute('''
                SELECT
                    COUNT(*) as total_properties_scraped,
                    COUNT(CASE WHEN extraction_success = 1 THEN 1 END) as successful_extractions,
                    AVG(data_quality_score) as average_quality,
                    COUNT(CASE WHEN data_quality_score < 0.7 THEN 1 END) as low_quality_count,
                    MAX(scraped_at) as last_scrape_date
                FROM individual_properties_scraped
            ''')
            overall_stats = cursor.fetchone()
            if overall_stats:
                stats['overall'] = dict(overall_stats)

            return stats

        except Exception as e:
            return {'success': False, 'error': str(e)}

        finally:
            self.db_manager.close_connection()

