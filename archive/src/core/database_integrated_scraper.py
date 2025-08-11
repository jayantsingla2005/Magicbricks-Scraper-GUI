#!/usr/bin/env python3
"""
Database-Integrated MagicBricks Scraper
Combines scraping with direct database storage for large-scale operations.
"""

import uuid
import time
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Selenium imports
from selenium.webdriver.support.ui import WebDriverWait

try:
    from .modern_scraper import ModernMagicBricksScraper
    from ..database.database_manager import DatabaseManager
    from ..models.property_model import PropertyModel
    from ..utils.logger import ScraperLogger
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent))
    from core.modern_scraper import ModernMagicBricksScraper
    from database.database_manager import DatabaseManager
    from models.property_model import PropertyModel
    from utils.logger import ScraperLogger


class DatabaseIntegratedScraper(ModernMagicBricksScraper):
    """
    Enhanced scraper with direct database integration
    Provides real-time storage and large-scale operation capabilities
    """
    
    def __init__(self, config_path: str = "config/scraper_config.json", 
                 db_path: str = "data/magicbricks.db", enable_db: bool = True):
        """Initialize database-integrated scraper"""
        super().__init__(config_path)
        
        # Database configuration
        self.enable_db = enable_db
        self.db_manager = None
        self.session_id = None
        
        # Initialize database if enabled
        if self.enable_db:
            try:
                self.db_manager = DatabaseManager(db_path)
                self.logger.logger.info(f"✅ Database integration enabled: {db_path}")
            except Exception as e:
                self.logger.logger.error(f"❌ Failed to initialize database: {str(e)}")
                self.enable_db = False
        
        # Enhanced statistics
        self.db_stats = {
            'properties_stored': 0,
            'storage_errors': 0,
            'batch_storage_times': []
        }
    
    def scrape_all_pages_with_db(self, start_page: int = 1, max_pages: Optional[int] = None,
                                store_batch_size: int = 30) -> Dict[str, Any]:
        """
        Scrape pages with real-time database storage
        
        Args:
            start_page: Starting page number
            max_pages: Maximum pages to scrape
            store_batch_size: Number of properties to store in each batch
        """
        
        # Create session ID
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Create database session if enabled
        if self.enable_db:
            session_config = {
                'start_page': start_page,
                'max_pages': max_pages,
                'store_batch_size': store_batch_size,
                'base_url': self.config['website']['base_url']
            }
            self.db_manager.create_session(self.session_id, session_config)
        
        self.logger.logger.info(f"🗄️ Starting database-integrated scraping (Session: {self.session_id})")
        
        try:
            # Initialize browser
            self.driver = self._setup_browser()
            self.wait = WebDriverWait(self.driver, self.config['delays']['element_wait_timeout'])

            # Set limits
            if max_pages is None:
                max_pages = self.config['website']['max_pages']

            self.current_page = start_page
            base_url = self.config['website']['base_url']
            
            # Storage batch
            property_batch = []
            
            self.logger.logger.info(f"🚀 Starting scraping from page {start_page} to {max_pages}")

            # Main scraping loop with database integration
            while self.current_page < start_page + max_pages:
                if self._should_stop_scraping():
                    break

                try:
                    # Construct page URL
                    if self.current_page == 1:
                        page_url = base_url
                    else:
                        page_url = f"{base_url}?page={self.current_page}"

                    self.logger.log_page_start(self.current_page, page_url)

                    # Scrape page
                    extracted_properties, properties_found, properties_extracted = self._scrape_page(page_url)

                    # Add to batch
                    property_batch.extend(extracted_properties)
                    
                    # Store batch if it reaches the batch size or it's the last page
                    if (len(property_batch) >= store_batch_size or 
                        self.current_page >= start_page + max_pages - 1):
                        
                        if property_batch and self.enable_db:
                            self._store_batch_to_db(property_batch, page_url)
                        
                        # Add to main collection
                        self.scraped_properties.extend(property_batch)
                        property_batch = []  # Clear batch

                    # Update totals
                    self.total_properties_scraped += properties_extracted

                    # Log page completion
                    valid_properties = len([p for p in extracted_properties if p.is_valid()])
                    self.logger.log_page_complete(
                        self.current_page, properties_found, properties_extracted, valid_properties
                    )

                    # Reset consecutive failures on success
                    self.consecutive_failures = 0

                    # Delay between pages
                    if self.current_page < start_page + max_pages - 1:
                        delay = random.uniform(
                            self.config['delays']['between_requests_min'],
                            self.config['delays']['between_requests_max']
                        )
                        time.sleep(delay)

                    self.current_page += 1

                except Exception as e:
                    self.consecutive_failures += 1
                    self.logger.log_error("PAGE_PROCESSING", f"Failed to process page {self.current_page}: {str(e)}",
                                        self.current_page)

                    # Check if we should stop
                    if self.consecutive_failures >= self.config['retry']['max_consecutive_failures']:
                        self.logger.logger.error(f"🛑 Too many consecutive failures ({self.consecutive_failures}). Stopping.")
                        break

                    # Move to next page anyway
                    self.current_page += 1

            # Store any remaining properties in batch
            if property_batch and self.enable_db:
                self._store_batch_to_db(property_batch, base_url)
                self.scraped_properties.extend(property_batch)

            # Final checkpoint
            self._save_checkpoint()

            # Export data (traditional files)
            output_files = self._export_data()

            # Update database session
            if self.enable_db:
                self._finalize_db_session(output_files)

            # Log session completion
            self.logger.log_session_complete(len(self.scraped_properties), output_files)

            return {
                'success': True,
                'session_id': self.session_id,
                'total_properties': len(self.scraped_properties),
                'valid_properties': len([p for p in self.scraped_properties if p.is_valid()]),
                'pages_processed': self.current_page - start_page,
                'output_files': output_files,
                'database_stats': self.db_stats,
                'database_enabled': self.enable_db
            }

        except Exception as e:
            self.logger.log_error("SCRAPING_SESSION", f"Critical error in database-integrated scraping: {str(e)}")
            
            # Update session with error
            if self.enable_db:
                self.db_manager.update_session(
                    self.session_id,
                    end_time=datetime.now(),
                    status='FAILED',
                    errors=self.db_stats['storage_errors']
                )
            
            return {
                'success': False,
                'error': str(e),
                'session_id': self.session_id,
                'total_properties': len(self.scraped_properties),
                'pages_processed': self.current_page - start_page if hasattr(self, 'current_page') else 0,
                'database_stats': self.db_stats
            }

        finally:
            # Cleanup
            if self.driver:
                try:
                    self.driver.quit()
                    self.logger.logger.info("🔧 Browser closed successfully")
                except Exception as e:
                    self.logger.logger.error(f"❌ Error closing browser: {str(e)}")
            
            # Close database connection
            if self.db_manager:
                self.db_manager.close()
    
    def _store_batch_to_db(self, properties: List[PropertyModel], source_url: str):
        """Store a batch of properties to database"""
        if not self.enable_db or not properties:
            return
        
        start_time = time.time()
        
        try:
            stored_count = self.db_manager.store_properties(
                properties, 
                self.session_id, 
                self.current_page, 
                source_url
            )
            
            storage_time = time.time() - start_time
            
            # Update statistics
            self.db_stats['properties_stored'] += stored_count
            self.db_stats['batch_storage_times'].append(storage_time)
            
            self.logger.logger.info(f"🗄️ Stored batch: {stored_count} properties in {storage_time:.2f}s")
            
        except Exception as e:
            self.db_stats['storage_errors'] += 1
            self.logger.log_error("DATABASE_STORAGE", f"Failed to store batch: {str(e)}")
    
    def _finalize_db_session(self, output_files: Dict[str, str]):
        """Finalize database session with completion stats"""
        if not self.enable_db:
            return
        
        try:
            # Calculate performance stats
            avg_storage_time = (sum(self.db_stats['batch_storage_times']) / 
                              len(self.db_stats['batch_storage_times'])) if self.db_stats['batch_storage_times'] else 0
            
            performance_stats = {
                'properties_stored': self.db_stats['properties_stored'],
                'storage_errors': self.db_stats['storage_errors'],
                'avg_batch_storage_time': avg_storage_time,
                'total_batches': len(self.db_stats['batch_storage_times'])
            }
            
            # Update session
            self.db_manager.update_session(
                self.session_id,
                end_time=datetime.now(),
                status='COMPLETED',
                total_pages=self.current_page - 1,
                total_properties=len(self.scraped_properties),
                valid_properties=len([p for p in self.scraped_properties if p.is_valid()]),
                errors=self.db_stats['storage_errors'],
                performance_stats=performance_stats
            )
            
            self.logger.logger.info(f"✅ Database session finalized: {self.session_id}")
            
        except Exception as e:
            self.logger.log_error("DATABASE_SESSION", f"Failed to finalize session: {str(e)}")
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        if not self.enable_db:
            return {'database_enabled': False}
        
        try:
            stats = self.db_manager.get_statistics()
            stats['current_session'] = {
                'session_id': self.session_id,
                'properties_stored': self.db_stats['properties_stored'],
                'storage_errors': self.db_stats['storage_errors']
            }
            return stats
            
        except Exception as e:
            self.logger.log_error("DATABASE_STATS", f"Failed to get database statistics: {str(e)}")
            return {'error': str(e)}
    
    def export_from_database(self, output_path: str, filters: Optional[Dict[str, Any]] = None) -> bool:
        """Export properties from database to CSV"""
        if not self.enable_db:
            self.logger.logger.warning("⚠️ Database not enabled - cannot export from database")
            return False
        
        try:
            success = self.db_manager.export_to_csv(output_path, filters)
            if success:
                self.logger.logger.info(f"✅ Exported properties from database to: {output_path}")
            return success
            
        except Exception as e:
            self.logger.log_error("DATABASE_EXPORT", f"Failed to export from database: {str(e)}")
            return False


# Export for easy import
__all__ = ['DatabaseIntegratedScraper']
