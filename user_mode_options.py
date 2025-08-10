#!/usr/bin/env python3
"""
User Mode Options Implementation
Create Incremental/Full/Date Range/Conservative mode options with user controls.
Provides flexible scraping modes based on user needs and confidence levels.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
from pathlib import Path
from enum import Enum


class ScrapingMode(Enum):
    """Enumeration of available scraping modes"""
    INCREMENTAL = "incremental"
    FULL = "full"
    DATE_RANGE = "date_range"
    CONSERVATIVE = "conservative"
    CUSTOM = "custom"


class UserModeOptions:
    """
    User mode options system for flexible incremental scraping
    """
    
    def __init__(self, db_path: str = 'magicbricks_enhanced.db'):
        """Initialize user mode options system"""
        
        self.db_path = db_path
        self.connection = None
        
        # Default mode configurations
        self.mode_configs = {
            ScrapingMode.INCREMENTAL: {
                'name': 'Incremental Mode',
                'description': 'Smart incremental scraping with 60-75% time savings',
                'stop_threshold_percentage': 80,
                'date_buffer_hours': 2,
                'max_pages': 100,
                'require_consecutive_old_pages': 2,
                'enable_url_validation': True,
                'enable_date_validation': True,
                'confidence_threshold': 0.7,
                'recommended_for': 'Regular updates, daily/weekly runs'
            },
            ScrapingMode.FULL: {
                'name': 'Full Scrape Mode',
                'description': 'Complete scraping of all properties (100% coverage)',
                'stop_threshold_percentage': 100,
                'date_buffer_hours': 0,
                'max_pages': 1000,
                'require_consecutive_old_pages': 999,
                'enable_url_validation': False,
                'enable_date_validation': False,
                'confidence_threshold': 1.0,
                'recommended_for': 'Initial setup, monthly comprehensive updates'
            },
            ScrapingMode.DATE_RANGE: {
                'name': 'Date Range Mode',
                'description': 'Scrape properties within specific date range',
                'stop_threshold_percentage': 90,
                'date_buffer_hours': 1,
                'max_pages': 200,
                'require_consecutive_old_pages': 3,
                'enable_url_validation': True,
                'enable_date_validation': True,
                'confidence_threshold': 0.8,
                'recommended_for': 'Targeted updates, specific time periods'
            },
            ScrapingMode.CONSERVATIVE: {
                'name': 'Conservative Mode',
                'description': 'Extra safe incremental scraping with higher coverage',
                'stop_threshold_percentage': 70,
                'date_buffer_hours': 4,
                'max_pages': 150,
                'require_consecutive_old_pages': 3,
                'enable_url_validation': True,
                'enable_date_validation': True,
                'confidence_threshold': 0.9,
                'recommended_for': 'Critical updates, when accuracy is paramount'
            },
            ScrapingMode.CUSTOM: {
                'name': 'Custom Mode',
                'description': 'User-defined parameters for specific needs',
                'stop_threshold_percentage': 80,
                'date_buffer_hours': 2,
                'max_pages': 100,
                'require_consecutive_old_pages': 2,
                'enable_url_validation': True,
                'enable_date_validation': True,
                'confidence_threshold': 0.7,
                'recommended_for': 'Advanced users with specific requirements'
            }
        }
        
        print("⚙️ User Mode Options System Initialized")
    
    def connect_db(self):
        """Connect to database"""
        
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False
    
    def get_available_modes(self) -> Dict[str, Dict[str, Any]]:
        """Get all available scraping modes with their configurations"""
        
        modes_info = {}
        
        for mode, config in self.mode_configs.items():
            modes_info[mode.value] = {
                'mode': mode.value,
                'name': config['name'],
                'description': config['description'],
                'recommended_for': config['recommended_for'],
                'configuration': {
                    'stop_threshold_percentage': config['stop_threshold_percentage'],
                    'max_pages': config['max_pages'],
                    'date_buffer_hours': config['date_buffer_hours'],
                    'confidence_threshold': config['confidence_threshold']
                }
            }
        
        return modes_info
    
    def create_scraping_session(self, city: str, mode: ScrapingMode, 
                              custom_config: Dict[str, Any] = None,
                              date_range: Tuple[datetime, datetime] = None) -> Dict[str, Any]:
        """Create a new scraping session with specified mode"""
        
        if not self.connect_db():
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            cursor = self.connection.cursor()
            
            # Get mode configuration
            if mode == ScrapingMode.CUSTOM and custom_config:
                config = custom_config
            else:
                config = self.mode_configs[mode].copy()
            
            # Handle date range mode
            if mode == ScrapingMode.DATE_RANGE and date_range:
                config['date_range_start'] = date_range[0]
                config['date_range_end'] = date_range[1]
            
            # Create session record
            session_data = {
                'start_timestamp': datetime.now(),
                'scrape_mode': mode.value,
                'city': city,
                'status': 'initialized',
                'configuration': json.dumps(config)
            }
            
            cursor.execute('''
                INSERT INTO scrape_sessions 
                (start_timestamp, scrape_mode, city, status, configuration, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_data['start_timestamp'],
                session_data['scrape_mode'],
                session_data['city'],
                session_data['status'],
                session_data['configuration'],
                datetime.now()
            ))
            
            session_id = cursor.lastrowid
            self.connection.commit()
            
            print(f"✅ Created scraping session {session_id} for {city} in {mode.value} mode")
            
            return {
                'success': True,
                'session_id': session_id,
                'mode': mode.value,
                'city': city,
                'configuration': config,
                'session_data': session_data
            }
            
        except Exception as e:
            self.connection.rollback()
            return {'success': False, 'error': str(e)}
        
        finally:
            if self.connection:
                self.connection.close()
    
    def get_mode_recommendations(self, city: str, last_scrape_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get mode recommendations based on scraping history and context"""
        
        recommendations = {
            'primary_recommendation': None,
            'alternative_recommendations': [],
            'reasoning': [],
            'estimated_time_savings': {},
            'confidence_levels': {}
        }
        
        # Analyze last scrape information
        if not last_scrape_info:
            # No previous scrape - recommend full mode
            recommendations['primary_recommendation'] = ScrapingMode.FULL.value
            recommendations['reasoning'].append('No previous scrape found - full scrape recommended for baseline')
            recommendations['estimated_time_savings'][ScrapingMode.FULL.value] = '0% (baseline)'
            recommendations['confidence_levels'][ScrapingMode.FULL.value] = 1.0
            
        else:
            last_scrape_date = last_scrape_info.get('last_scrape_date')
            days_since_last_scrape = (datetime.now() - last_scrape_date).days if last_scrape_date else 999
            
            if days_since_last_scrape <= 1:
                # Recent scrape - incremental mode
                recommendations['primary_recommendation'] = ScrapingMode.INCREMENTAL.value
                recommendations['reasoning'].append(f'Last scrape was {days_since_last_scrape} day(s) ago - incremental mode optimal')
                recommendations['estimated_time_savings'][ScrapingMode.INCREMENTAL.value] = '60-75%'
                recommendations['confidence_levels'][ScrapingMode.INCREMENTAL.value] = 0.9
                
                # Alternative: conservative mode
                recommendations['alternative_recommendations'].append(ScrapingMode.CONSERVATIVE.value)
                recommendations['estimated_time_savings'][ScrapingMode.CONSERVATIVE.value] = '50-65%'
                recommendations['confidence_levels'][ScrapingMode.CONSERVATIVE.value] = 0.95
                
            elif days_since_last_scrape <= 7:
                # Weekly scrape - conservative mode
                recommendations['primary_recommendation'] = ScrapingMode.CONSERVATIVE.value
                recommendations['reasoning'].append(f'Last scrape was {days_since_last_scrape} day(s) ago - conservative mode recommended')
                recommendations['estimated_time_savings'][ScrapingMode.CONSERVATIVE.value] = '50-65%'
                recommendations['confidence_levels'][ScrapingMode.CONSERVATIVE.value] = 0.85
                
                # Alternative: incremental mode
                recommendations['alternative_recommendations'].append(ScrapingMode.INCREMENTAL.value)
                recommendations['estimated_time_savings'][ScrapingMode.INCREMENTAL.value] = '60-75%'
                recommendations['confidence_levels'][ScrapingMode.INCREMENTAL.value] = 0.75
                
            else:
                # Old scrape - full mode
                recommendations['primary_recommendation'] = ScrapingMode.FULL.value
                recommendations['reasoning'].append(f'Last scrape was {days_since_last_scrape} day(s) ago - full scrape recommended')
                recommendations['estimated_time_savings'][ScrapingMode.FULL.value] = '0% (comprehensive)'
                recommendations['confidence_levels'][ScrapingMode.FULL.value] = 1.0
        
        return recommendations
    
    def validate_mode_configuration(self, mode: ScrapingMode, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mode configuration parameters"""
        
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        # Validate stop threshold
        stop_threshold = config.get('stop_threshold_percentage', 80)
        if stop_threshold < 50:
            validation_result['warnings'].append('Stop threshold below 50% may miss many properties')
        elif stop_threshold > 95:
            validation_result['warnings'].append('Stop threshold above 95% may not provide significant time savings')
        
        # Validate max pages
        max_pages = config.get('max_pages', 100)
        if max_pages < 10:
            validation_result['errors'].append('Max pages too low - may not find sufficient properties')
            validation_result['is_valid'] = False
        elif max_pages > 500:
            validation_result['warnings'].append('Max pages very high - may take long time even in incremental mode')
        
        # Validate date buffer
        date_buffer = config.get('date_buffer_hours', 2)
        if date_buffer < 0:
            validation_result['errors'].append('Date buffer cannot be negative')
            validation_result['is_valid'] = False
        elif date_buffer > 24:
            validation_result['warnings'].append('Date buffer over 24 hours may be too conservative')
        
        # Mode-specific validations
        if mode == ScrapingMode.INCREMENTAL:
            if not config.get('enable_date_validation', True):
                validation_result['warnings'].append('Date validation disabled in incremental mode may reduce accuracy')
        
        elif mode == ScrapingMode.CONSERVATIVE:
            if stop_threshold > 80:
                validation_result['suggestions'].append('Consider lowering stop threshold for more conservative approach')
        
        return validation_result
    
    def get_session_history(self, city: str = None, limit: int = 10) -> Dict[str, Any]:
        """Get scraping session history"""
        
        if not self.connect_db():
            return {'success': False, 'error': 'Database connection failed'}
        
        try:
            cursor = self.connection.cursor()
            
            if city:
                cursor.execute('''
                    SELECT session_id, start_timestamp, end_timestamp, scrape_mode, 
                           pages_scraped, properties_found, status, stop_reason
                    FROM scrape_sessions 
                    WHERE city = ?
                    ORDER BY start_timestamp DESC 
                    LIMIT ?
                ''', (city, limit))
            else:
                cursor.execute('''
                    SELECT session_id, start_timestamp, end_timestamp, scrape_mode, city,
                           pages_scraped, properties_found, status, stop_reason
                    FROM scrape_sessions 
                    ORDER BY start_timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                if city:
                    session_id, start_time, end_time, mode, pages, properties, status, stop_reason = row
                    session_city = city
                else:
                    session_id, start_time, end_time, mode, session_city, pages, properties, status, stop_reason = row
                
                session_info = {
                    'session_id': session_id,
                    'start_timestamp': start_time,
                    'end_timestamp': end_time,
                    'scrape_mode': mode,
                    'city': session_city,
                    'pages_scraped': pages or 0,
                    'properties_found': properties or 0,
                    'status': status,
                    'stop_reason': stop_reason
                }
                
                # Calculate duration if session completed
                if end_time and start_time:
                    start_dt = datetime.fromisoformat(start_time)
                    end_dt = datetime.fromisoformat(end_time)
                    duration = (end_dt - start_dt).total_seconds()
                    session_info['duration_seconds'] = duration
                    session_info['duration_formatted'] = f"{duration//60:.0f}m {duration%60:.0f}s"
                
                sessions.append(session_info)
            
            return {
                'success': True,
                'sessions': sessions,
                'total_sessions': len(sessions)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        finally:
            if self.connection:
                self.connection.close()
    
    def test_user_mode_options(self) -> Dict[str, Any]:
        """Test the user mode options system"""
        
        print("🧪 TESTING USER MODE OPTIONS SYSTEM")
        print("="*50)
        
        test_results = {
            'modes_available': 0,
            'sessions_created': 0,
            'validations_passed': 0,
            'recommendations_generated': 0,
            'test_success': False
        }
        
        # Test 1: Get available modes
        print("📋 Testing available modes...")
        modes = self.get_available_modes()
        test_results['modes_available'] = len(modes)
        print(f"   ✅ Found {len(modes)} available modes")
        
        # Test 2: Create sessions for different modes
        print("\n📋 Testing session creation...")
        test_modes = [ScrapingMode.INCREMENTAL, ScrapingMode.CONSERVATIVE, ScrapingMode.FULL]
        
        for mode in test_modes:
            session_result = self.create_scraping_session('test_city', mode)
            if session_result['success']:
                test_results['sessions_created'] += 1
                print(f"   ✅ Created session for {mode.value} mode")
            else:
                print(f"   ❌ Failed to create session for {mode.value} mode")
        
        # Test 3: Validate configurations
        print("\n📋 Testing configuration validation...")
        test_configs = [
            {'stop_threshold_percentage': 80, 'max_pages': 100, 'date_buffer_hours': 2},
            {'stop_threshold_percentage': 30, 'max_pages': 5, 'date_buffer_hours': -1},  # Should have errors
            {'stop_threshold_percentage': 70, 'max_pages': 150, 'date_buffer_hours': 4}
        ]
        
        for config in test_configs:
            validation = self.validate_mode_configuration(ScrapingMode.INCREMENTAL, config)
            if validation['is_valid'] or len(validation['warnings']) > 0:
                test_results['validations_passed'] += 1
        
        print(f"   ✅ Validated {test_results['validations_passed']}/{len(test_configs)} configurations")
        
        # Test 4: Get recommendations
        print("\n📋 Testing mode recommendations...")
        
        # Test with no previous scrape
        recommendations = self.get_mode_recommendations('test_city')
        if recommendations['primary_recommendation']:
            test_results['recommendations_generated'] += 1
            print(f"   ✅ Generated recommendation: {recommendations['primary_recommendation']}")
        
        # Test with recent scrape
        last_scrape_info = {'last_scrape_date': datetime.now() - timedelta(hours=12)}
        recommendations = self.get_mode_recommendations('test_city', last_scrape_info)
        if recommendations['primary_recommendation']:
            test_results['recommendations_generated'] += 1
            print(f"   ✅ Generated recommendation for recent scrape: {recommendations['primary_recommendation']}")
        
        # Test 5: Get session history
        print("\n📋 Testing session history...")
        history = self.get_session_history('test_city', limit=5)
        if history['success']:
            print(f"   ✅ Retrieved {history['total_sessions']} session records")
        
        # Overall test success
        test_results['test_success'] = (
            test_results['modes_available'] >= 5 and
            test_results['sessions_created'] >= 2 and
            test_results['validations_passed'] >= 2 and
            test_results['recommendations_generated'] >= 2
        )
        
        print(f"\n📊 USER MODE OPTIONS TEST RESULTS")
        print("="*50)
        print(f"✅ Available modes: {test_results['modes_available']}")
        print(f"✅ Sessions created: {test_results['sessions_created']}")
        print(f"✅ Validations passed: {test_results['validations_passed']}")
        print(f"✅ Recommendations generated: {test_results['recommendations_generated']}")
        print(f"🎯 Overall test success: {test_results['test_success']}")
        
        return test_results


def main():
    """Main function for user mode options testing"""
    
    try:
        mode_options = UserModeOptions()
        test_results = mode_options.test_user_mode_options()
        
        if test_results['test_success']:
            print("\n✅ User mode options system test successful!")
            return True
        else:
            print("\n⚠️ User mode options system needs improvement!")
            return False
            
    except Exception as e:
        print(f"❌ User mode options system test failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
