#!/usr/bin/env python3
"""
Individual Property Tracking System
Handles duplicate detection and tracking for individual property page scraping

REFACTORED: Composition/Facade pattern using specialized modules:
- property_database_manager.py: DB connections and schema
- property_quality_scorer.py: Quality scoring
- property_tracking_operations.py: Core tracking logic
- property_statistics.py: Statistics retrieval and reporting

Maintains 100% backward compatibility with original interface.
"""

from typing import List, Dict, Any
from property_database_manager import PropertyDatabaseManager
from property_quality_scorer import PropertyQualityScorer
from property_tracking_operations import PropertyTrackingOperations
from property_statistics import PropertyStatistics


class IndividualPropertyTracker:
    """
    Comprehensive tracking system for individual property scraping (Facade)
    Prevents duplicate scraping and manages property data persistence
    """

    def __init__(self, db_path: str = 'magicbricks_enhanced.db'):
        """Initialize individual property tracking system with modular components"""

        self.db_path = db_path

        # Tracking configuration (unchanged)
        self.config = {
            'enable_duplicate_detection': True,
            'force_rescrape_days': 30,  # Re-scrape after 30 days
            'max_retry_attempts': 3,
            'quality_threshold': 0.7,   # Minimum quality score
            'enable_change_detection': True
        }

        # Initialize modular components
        self.db_manager = PropertyDatabaseManager(db_path)
        self.quality_scorer = PropertyQualityScorer()
        self.operations = PropertyTrackingOperations(self.db_manager, self.quality_scorer, self.config)
        self.statistics = PropertyStatistics(self.db_manager)

        # Statistics tracking (backward-compatible attribute)
        self.stats = self.operations.stats

        # Initialize database schema
        self.setup_database_schema()

    # Backward-compatible methods delegating to modules
    def connect_db(self) -> bool:
        """Establish database connection (delegates to db_manager)"""
        return self.db_manager.connect_db()

    def setup_database_schema(self):
        """Create necessary tables for individual property tracking (delegates to db_manager)"""
        return self.db_manager.setup_database_schema()

    def generate_url_hash(self, url: str) -> str:
        """Generate unique hash for URL (delegates to operations)"""
        return self.operations.generate_url_hash(url)

    def normalize_url(self, url: str) -> str:
        """Normalize URL for consistent comparison (delegates to operations)"""
        return self.operations.normalize_url(url)

    def create_scraping_session(self, session_name: str, total_urls: int, config: Dict[str, Any] = None) -> int:
        """Create a new individual property scraping session (delegates to operations)"""
        return self.operations.create_scraping_session(session_name, total_urls, config)

    def filter_urls_for_scraping(self, property_urls: List[str],
                                force_rescrape: bool = False,
                                quality_threshold: float = None) -> Dict[str, Any]:
        """Filter URLs and determine which need scraping (delegates to operations)"""
        return self.operations.filter_urls_for_scraping(property_urls, force_rescrape, quality_threshold)

    def is_property_scraped(self, property_url: str, session_id: int | None = None) -> bool:
        """Backward-compatible check: has this property URL already been scraped?"""
        if not self.db_manager.connect_db():
            return False
        try:
            cursor = self.db_manager.connection.cursor()
            normalized_url = self.normalize_url(property_url)
            url_hash = self.generate_url_hash(normalized_url)
            cursor.execute(
                '''
                SELECT extraction_success FROM individual_properties_scraped
                WHERE url_hash = ? OR property_url = ?
                ''',
                (url_hash, normalized_url)
            )
            row = cursor.fetchone()
            return bool(row and (row[0] == 1 or row[0] is True))
        except Exception:
            return False
        finally:
            self.db_manager.close_connection()

    def mark_property_scraped(self, property_url: str, session_id: int | None = None) -> bool:
        """Backward-compatible mark: record that this URL has been scraped (minimal upsert)."""
        if not self.db_manager.connect_db():
            return False
        try:
            cursor = self.db_manager.connection.cursor()
            from datetime import datetime
            normalized_url = self.normalize_url(property_url)
            url_hash = self.generate_url_hash(normalized_url)
            now = datetime.now()
            # Check existing
            cursor.execute(
                '''SELECT 1 FROM individual_properties_scraped WHERE url_hash = ? OR property_url = ?''',
                (url_hash, normalized_url)
            )
            exists = cursor.fetchone() is not None
            if exists:
                cursor.execute(
                    '''
                    UPDATE individual_properties_scraped
                    SET scraped_at = ?, scraping_session_id = COALESCE(?, scraping_session_id),
                        extraction_success = 1, updated_at = ?
                    WHERE url_hash = ? OR property_url = ?
                    ''',
                    (now, session_id, now, url_hash, normalized_url)
                )
            else:
                cursor.execute(
                    '''
                    INSERT INTO individual_properties_scraped
                    (property_url, property_id, url_hash, scraped_at, scraping_session_id,
                     data_quality_score, extraction_success, retry_count, updated_at)
                    VALUES (?, NULL, ?, ?, ?, 0.0, 1, 0, ?)
                    ''',
                    (normalized_url, url_hash, now, session_id, now)
                )
            self.db_manager.connection.commit()
            return True
        except Exception:
            return False
        finally:
            self.db_manager.close_connection()

    def track_scraped_property(self, property_url: str, property_data: Dict[str, Any],
                              session_id: int, quality_score: float = None) -> bool:
        """Track a successfully scraped individual property (delegates to operations)"""
        return self.operations.track_scraped_property(property_url, property_data, session_id, quality_score)

    def calculate_data_quality_score(self, property_data: Dict[str, Any]) -> float:
        """Calculate data quality score (delegates to quality_scorer)"""
        return self.quality_scorer.calculate_quality_score(property_data)

    def get_scraping_statistics(self, session_id: int = None) -> Dict[str, Any]:
        """Get comprehensive scraping statistics (delegates to statistics module)"""
        return self.statistics.get_scraping_statistics(session_id)


# Example usage and testing
if __name__ == "__main__":
    # Initialize tracker
    tracker = IndividualPropertyTracker()

    # Test URL filtering
    test_urls = [
        "https://www.magicbricks.com/property-detail-1",
        "https://www.magicbricks.com/property-detail-2",
        "https://www.magicbricks.com/property-detail-3"
    ]

    # Create test session
    session_id = tracker.create_scraping_session("Test Session", len(test_urls))

    # Filter URLs
    filter_result = tracker.filter_urls_for_scraping(test_urls)
    print(f"Filter result: {filter_result}")

    # Get statistics
    stats = tracker.get_scraping_statistics()
    print(f"Statistics: {stats}")
