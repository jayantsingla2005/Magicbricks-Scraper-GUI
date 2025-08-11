"""
Comprehensive Logging System for MagicBricks Scraper
Provides detailed progress tracking, performance metrics, and error reporting
"""

import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
from pathlib import Path


class ScraperLogger:
    """
    Advanced logging system with detailed progress tracking and performance metrics
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.start_time = datetime.now()
        self.page_start_time = None
        self.session_stats = {
            'total_pages_processed': 0,
            'total_properties_extracted': 0,
            'total_properties_valid': 0,
            'total_errors': 0,
            'total_retries': 0,
            'pages_with_errors': 0,
            'average_page_time': 0,
            'average_properties_per_page': 0,
            'data_quality_scores': []
        }
        
        self._setup_logging()
        self._log_session_start()
    
    def _setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Create output directory if it doesn't exist
        output_dir = Path(self.config['output']['export_directory'])
        output_dir.mkdir(exist_ok=True)
        
        # Generate log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = self.config['output']['log_filename'].format(timestamp=timestamp)
        log_path = output_dir / log_filename
        
        # Configure root logger
        self.logger = logging.getLogger('MagicBricksScraper')
        self.logger.setLevel(getattr(logging, self.config['logging']['level']))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            self.config['logging']['format'],
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        if self.config['logging']['console_output']:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # File handler
        if self.config['logging']['file_output']:
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        # Store log path for reference
        self.log_file_path = log_path
    
    def _log_session_start(self):
        """Log session initialization details"""
        self.logger.info("=" * 80)
        self.logger.info("🚀 MAGICBRICKS SCRAPER SESSION STARTED")
        self.logger.info("=" * 80)
        self.logger.info(f"📅 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"🎯 Target URL: {self.config['website']['base_url']}")
        self.logger.info(f"📊 Max Pages: {self.config['website']['max_pages']}")
        self.logger.info(f"🏠 Properties per Page: {self.config['website']['properties_per_page']}")
        self.logger.info(f"💾 Output Directory: {self.config['output']['export_directory']}")
        self.logger.info(f"📝 Log File: {self.log_file_path}")
        self.logger.info("-" * 80)
    
    def log_page_start(self, page_number: int, page_url: str):
        """Log start of page processing"""
        self.page_start_time = datetime.now()
        self.logger.info(f"📄 PAGE {page_number} - PROCESSING STARTED")
        self.logger.info(f"🔗 URL: {page_url}")
        
        if self.config['logging']['detailed_progress']:
            elapsed = self.page_start_time - self.start_time
            self.logger.info(f"⏱️  Session Elapsed: {self._format_duration(elapsed)}")
            
            if self.session_stats['total_pages_processed'] > 0:
                avg_time = self.session_stats['average_page_time']
                remaining_pages = self.config['website']['max_pages'] - page_number
                estimated_remaining = timedelta(seconds=avg_time * remaining_pages)
                self.logger.info(f"⏳ Estimated Remaining: {self._format_duration(estimated_remaining)}")
    
    def log_page_complete(self, page_number: int, properties_found: int, properties_extracted: int, 
                         properties_valid: int, errors: int = 0):
        """Log completion of page processing with detailed metrics"""
        if self.page_start_time is None:
            self.page_start_time = datetime.now()
        
        page_duration = datetime.now() - self.page_start_time
        page_time_seconds = page_duration.total_seconds()
        
        # Update session statistics
        self.session_stats['total_pages_processed'] += 1
        self.session_stats['total_properties_extracted'] += properties_extracted
        self.session_stats['total_properties_valid'] += properties_valid
        self.session_stats['total_errors'] += errors
        
        if errors > 0:
            self.session_stats['pages_with_errors'] += 1
        
        # Calculate averages
        total_pages = self.session_stats['total_pages_processed']
        self.session_stats['average_page_time'] = (
            (self.session_stats['average_page_time'] * (total_pages - 1) + page_time_seconds) / total_pages
        )
        
        if properties_found > 0:
            extraction_rate = (properties_extracted / properties_found) * 100
        else:
            extraction_rate = 0
        
        if properties_extracted > 0:
            validation_rate = (properties_valid / properties_extracted) * 100
        else:
            validation_rate = 0
        
        # Log page completion
        self.logger.info(f"✅ PAGE {page_number} - COMPLETED")
        self.logger.info(f"⏱️  Page Time: {self._format_duration(page_duration)}")
        self.logger.info(f"🏠 Properties Found: {properties_found}")
        self.logger.info(f"📊 Properties Extracted: {properties_extracted} ({extraction_rate:.1f}%)")
        self.logger.info(f"✔️  Properties Valid: {properties_valid} ({validation_rate:.1f}%)")
        
        if errors > 0:
            self.logger.warning(f"⚠️  Errors on Page: {errors}")
        
        # Session totals
        self.logger.info(f"📈 SESSION TOTALS:")
        self.logger.info(f"   📄 Pages Processed: {self.session_stats['total_pages_processed']}")
        self.logger.info(f"   🏠 Total Properties: {self.session_stats['total_properties_extracted']}")
        self.logger.info(f"   ✔️  Valid Properties: {self.session_stats['total_properties_valid']}")
        self.logger.info(f"   ⚠️  Total Errors: {self.session_stats['total_errors']}")
        self.logger.info(f"   ⏱️  Avg Page Time: {self.session_stats['average_page_time']:.1f}s")
        self.logger.info("-" * 60)
    
    def log_property_extraction(self, property_data: Dict[str, Any], position: int, success: bool = True):
        """Log individual property extraction details"""
        if not self.config['logging']['detailed_progress']:
            return
        
        if success:
            title = property_data.get('title', 'Unknown')[:50]
            price = property_data.get('price', 'N/A')
            quality_score = property_data.get('data_quality_score', 0)
            
            self.logger.debug(f"   🏠 Property {position}: {title}... | {price} | Quality: {quality_score:.1f}%")
            
            if quality_score:
                self.session_stats['data_quality_scores'].append(quality_score)
        else:
            self.logger.debug(f"   ❌ Property {position}: Extraction failed")
    
    def log_error(self, error_type: str, error_message: str, page_number: Optional[int] = None, 
                  property_position: Optional[int] = None, retry_count: int = 0):
        """Log errors with context and retry information"""
        context = []
        if page_number is not None:
            context.append(f"Page {page_number}")
        if property_position is not None:
            context.append(f"Property {property_position}")
        if retry_count > 0:
            context.append(f"Retry {retry_count}")
        
        context_str = " | ".join(context) if context else "General"
        
        self.logger.error(f"❌ ERROR [{error_type}] {context_str}: {error_message}")
        
        if retry_count > 0:
            self.session_stats['total_retries'] += 1
    
    def log_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """Log checkpoint creation"""
        self.logger.info(f"💾 CHECKPOINT SAVED")
        self.logger.info(f"   📄 Page: {checkpoint_data.get('current_page', 'Unknown')}")
        self.logger.info(f"   🏠 Properties: {checkpoint_data.get('total_properties', 'Unknown')}")
        self.logger.info(f"   📁 File: {checkpoint_data.get('checkpoint_file', 'Unknown')}")
    
    def log_session_complete(self, total_properties: int, output_files: Dict[str, str]):
        """Log session completion with comprehensive summary"""
        end_time = datetime.now()
        total_duration = end_time - self.start_time
        
        # Calculate final statistics
        avg_quality = sum(self.session_stats['data_quality_scores']) / len(self.session_stats['data_quality_scores']) if self.session_stats['data_quality_scores'] else 0
        success_rate = (self.session_stats['total_properties_valid'] / self.session_stats['total_properties_extracted'] * 100) if self.session_stats['total_properties_extracted'] > 0 else 0
        error_rate = (self.session_stats['total_errors'] / self.session_stats['total_properties_extracted'] * 100) if self.session_stats['total_properties_extracted'] > 0 else 0
        
        self.logger.info("=" * 80)
        self.logger.info("🎉 SCRAPING SESSION COMPLETED SUCCESSFULLY")
        self.logger.info("=" * 80)
        self.logger.info(f"⏱️  Total Duration: {self._format_duration(total_duration)}")
        self.logger.info(f"📄 Pages Processed: {self.session_stats['total_pages_processed']}")
        self.logger.info(f"🏠 Properties Extracted: {self.session_stats['total_properties_extracted']}")
        self.logger.info(f"✔️  Valid Properties: {self.session_stats['total_properties_valid']}")
        self.logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        self.logger.info(f"⚠️  Error Rate: {error_rate:.1f}%")
        self.logger.info(f"🎯 Average Quality Score: {avg_quality:.1f}%")
        self.logger.info(f"⏱️  Average Page Time: {self.session_stats['average_page_time']:.1f}s")
        
        self.logger.info("\n📁 OUTPUT FILES:")
        for file_type, file_path in output_files.items():
            self.logger.info(f"   {file_type}: {file_path}")
        
        self.logger.info("=" * 80)
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration in human-readable format"""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return self.session_stats.copy()
    
    def export_session_log(self, export_path: str):
        """Export detailed session log as JSON"""
        session_data = {
            'session_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
                'config': self.config
            },
            'statistics': self.session_stats,
            'log_file': str(self.log_file_path)
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📊 Session log exported to: {export_path}")


# Export for easy import
__all__ = ['ScraperLogger']
