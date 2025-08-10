#!/usr/bin/env python3
"""
Date Parsing System Implementation
Create robust parser for 'today', 'X hours ago', 'X days ago' text patterns.
Based on empirical research findings from MagicBricks.
"""

import re
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
from pathlib import Path


class DateParsingSystem:
    """
    Robust date parsing system for MagicBricks property posting dates
    """
    
    def __init__(self, db_path: str = 'magicbricks_enhanced.db'):
        """Initialize date parsing system"""
        
        self.db_path = db_path
        self.connection = None
        
        # Date patterns discovered through research
        self.date_patterns = [
            # Hours ago patterns
            (r'(\d+)\s+hours?\s+ago', 'hours_ago', 1.0),
            (r'Posted:?\s*(\d+)\s+hours?\s+ago', 'posted_hours_ago', 1.0),
            
            # Days ago patterns  
            (r'(\d+)\s+days?\s+ago', 'days_ago', 1.0),
            (r'Posted:?\s*(\d+)\s+days?\s+ago', 'posted_days_ago', 1.0),
            
            # Weeks ago patterns
            (r'(\d+)\s+weeks?\s+ago', 'weeks_ago', 1.0),
            (r'Posted:?\s*(\d+)\s+weeks?\s+ago', 'posted_weeks_ago', 1.0),
            
            # Months ago patterns
            (r'(\d+)\s+months?\s+ago', 'months_ago', 0.9),
            (r'Posted:?\s*(\d+)\s+months?\s+ago', 'posted_months_ago', 0.9),
            
            # Today patterns
            (r'\btoday\b', 'today', 1.0),
            (r'Posted:?\s*today', 'posted_today', 1.0),
            
            # Yesterday patterns
            (r'\byesterday\b', 'yesterday', 1.0),
            (r'Posted:?\s*yesterday', 'posted_yesterday', 1.0),
            
            # Absolute date patterns (lower confidence)
            (r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', 'absolute_date', 0.7),
            (r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{2,4})', 'month_date', 0.8)
        ]
        
        # Parsing statistics
        self.parsing_stats = {
            'total_attempts': 0,
            'successful_parses': 0,
            'pattern_usage': {},
            'confidence_distribution': {}
        }
        
        print("📅 Date Parsing System Initialized")
    
    def connect_db(self):
        """Connect to database"""
        
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False
    
    def parse_posting_date(self, text: str, extraction_date: datetime = None) -> Dict[str, Any]:
        """Parse posting date from text using robust pattern matching"""
        
        if extraction_date is None:
            extraction_date = datetime.now()
        
        self.parsing_stats['total_attempts'] += 1
        
        parse_result = {
            'raw_text': text,
            'pattern_matched': None,
            'pattern_type': None,
            'numeric_value': None,
            'parsed_datetime': None,
            'confidence_score': 0.0,
            'parsing_method': 'pattern_matching',
            'extraction_date': extraction_date,
            'success': False,
            'error': None
        }
        
        try:
            if not text or not isinstance(text, str):
                parse_result['error'] = 'Invalid input text'
                return parse_result
            
            # Clean text for better matching
            cleaned_text = text.strip().lower()
            
            # Try each pattern in order of confidence
            for pattern, pattern_type, confidence in self.date_patterns:
                matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
                
                if matches:
                    parse_result['pattern_matched'] = pattern
                    parse_result['pattern_type'] = pattern_type
                    parse_result['confidence_score'] = confidence
                    
                    # Update statistics
                    self.parsing_stats['pattern_usage'][pattern_type] = \
                        self.parsing_stats['pattern_usage'].get(pattern_type, 0) + 1
                    
                    # Parse based on pattern type
                    parsed_datetime = self._parse_by_pattern_type(
                        pattern_type, matches[0], extraction_date
                    )
                    
                    if parsed_datetime:
                        parse_result['parsed_datetime'] = parsed_datetime
                        parse_result['success'] = True
                        self.parsing_stats['successful_parses'] += 1
                        
                        # Extract numeric value if applicable
                        if pattern_type in ['hours_ago', 'posted_hours_ago', 'days_ago', 'posted_days_ago',
                                          'weeks_ago', 'posted_weeks_ago', 'months_ago', 'posted_months_ago']:
                            if isinstance(matches[0], str) and matches[0].isdigit():
                                parse_result['numeric_value'] = int(matches[0])
                            elif isinstance(matches[0], tuple) and len(matches[0]) > 0:
                                if str(matches[0][0]).isdigit():
                                    parse_result['numeric_value'] = int(matches[0][0])
                    
                    break
            
            if not parse_result['success']:
                parse_result['error'] = 'No matching date patterns found'
            
            return parse_result
            
        except Exception as e:
            parse_result['error'] = f'Parsing error: {str(e)}'
            return parse_result
    
    def _parse_by_pattern_type(self, pattern_type: str, match_data: Any, reference_date: datetime) -> Optional[datetime]:
        """Parse datetime based on pattern type and match data"""
        
        try:
            if pattern_type in ['hours_ago', 'posted_hours_ago']:
                if isinstance(match_data, str) and match_data.isdigit():
                    hours = int(match_data)
                elif isinstance(match_data, tuple) and len(match_data) > 0:
                    hours = int(match_data[0]) if str(match_data[0]).isdigit() else 0
                else:
                    hours = int(match_data) if str(match_data).isdigit() else 0
                return reference_date - timedelta(hours=hours)
            
            elif pattern_type in ['days_ago', 'posted_days_ago']:
                if isinstance(match_data, str) and match_data.isdigit():
                    days = int(match_data)
                elif isinstance(match_data, tuple) and len(match_data) > 0:
                    days = int(match_data[0]) if str(match_data[0]).isdigit() else 0
                else:
                    days = int(match_data) if str(match_data).isdigit() else 0
                return reference_date - timedelta(days=days)
            
            elif pattern_type in ['weeks_ago', 'posted_weeks_ago']:
                weeks = int(match_data) if str(match_data).isdigit() else 0
                return reference_date - timedelta(weeks=weeks)
            
            elif pattern_type in ['months_ago', 'posted_months_ago']:
                months = int(match_data) if str(match_data).isdigit() else 0
                return reference_date - timedelta(days=months*30)  # Approximate
            
            elif pattern_type in ['today', 'posted_today']:
                return reference_date.replace(hour=12, minute=0, second=0, microsecond=0)
            
            elif pattern_type in ['yesterday', 'posted_yesterday']:
                return reference_date.replace(hour=12, minute=0, second=0, microsecond=0) - timedelta(days=1)
            
            elif pattern_type == 'absolute_date':
                # Handle DD/MM/YYYY or MM/DD/YYYY formats
                if isinstance(match_data, tuple) and len(match_data) >= 3:
                    day, month, year = match_data[0], match_data[1], match_data[2]
                    
                    # Convert to integers
                    day = int(day)
                    month = int(month)
                    year = int(year)
                    
                    # Handle 2-digit years
                    if year < 100:
                        year += 2000 if year < 50 else 1900
                    
                    # Try both DD/MM/YYYY and MM/DD/YYYY
                    try:
                        return datetime(year, month, day, 12, 0, 0)
                    except ValueError:
                        try:
                            return datetime(year, day, month, 12, 0, 0)
                        except ValueError:
                            return None
            
            elif pattern_type == 'month_date':
                # Handle "15 Jan 2024" format
                if isinstance(match_data, tuple) and len(match_data) >= 3:
                    day, month_str, year = match_data[0], match_data[1], match_data[2]
                    
                    month_map = {
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                    }
                    
                    month = month_map.get(month_str.lower()[:3])
                    if month:
                        day = int(day)
                        year = int(year)
                        if year < 100:
                            year += 2000 if year < 50 else 1900
                        
                        return datetime(year, month, day, 12, 0, 0)
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error parsing pattern type {pattern_type}: {str(e)}")
            return None
    
    def batch_parse_dates(self, text_list: List[str], extraction_date: datetime = None) -> List[Dict[str, Any]]:
        """Parse multiple date texts in batch"""
        
        print(f"📅 Batch parsing {len(text_list)} date texts...")
        
        results = []
        for i, text in enumerate(text_list):
            result = self.parse_posting_date(text, extraction_date)
            results.append(result)
            
            if (i + 1) % 100 == 0:
                print(f"   ✅ Processed {i + 1}/{len(text_list)} texts")
        
        return results
    
    def save_parsing_results_to_db(self, parsing_results: List[Dict[str, Any]], property_urls: List[str] = None):
        """Save parsing results to database"""
        
        if not self.connect_db():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            print(f"💾 Saving {len(parsing_results)} parsing results to database...")
            
            for i, result in enumerate(parsing_results):
                property_url = property_urls[i] if property_urls and i < len(property_urls) else f"test_url_{i}"
                
                cursor.execute('''
                    INSERT INTO property_posting_dates 
                    (property_url, posting_date_text, parsed_posting_date, extraction_date, 
                     confidence_score, parsing_method, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    property_url,
                    result['raw_text'],
                    result['parsed_datetime'],
                    result['extraction_date'],
                    result['confidence_score'],
                    result['parsing_method'],
                    datetime.now()
                ))
            
            self.connection.commit()
            print(f"✅ Saved {len(parsing_results)} parsing results to database")
            return True
            
        except Exception as e:
            print(f"❌ Error saving parsing results: {str(e)}")
            self.connection.rollback()
            return False
        
        finally:
            if self.connection:
                self.connection.close()
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive parsing statistics"""
        
        success_rate = (self.parsing_stats['successful_parses'] / 
                       max(self.parsing_stats['total_attempts'], 1)) * 100
        
        stats = {
            'total_attempts': self.parsing_stats['total_attempts'],
            'successful_parses': self.parsing_stats['successful_parses'],
            'success_rate_percentage': round(success_rate, 2),
            'pattern_usage': self.parsing_stats['pattern_usage'],
            'most_common_pattern': max(self.parsing_stats['pattern_usage'].items(), 
                                     key=lambda x: x[1])[0] if self.parsing_stats['pattern_usage'] else None
        }
        
        return stats
    
    def test_date_parsing_system(self) -> Dict[str, Any]:
        """Test the date parsing system with sample data"""
        
        print("🧪 TESTING DATE PARSING SYSTEM")
        print("="*50)
        
        # Test cases based on research findings
        test_cases = [
            "10 hours ago",
            "8 hours ago", 
            "9 hours ago",
            "2 days ago",
            "1 week ago",
            "today",
            "yesterday",
            "Posted: 5 hours ago",
            "Posted: today",
            "Posted: 3 days ago",
            "15/01/2024",
            "15 Jan 2024",
            "invalid date text",
            "",
            "some random text with no dates"
        ]
        
        test_results = {
            'test_cases_run': len(test_cases),
            'successful_parses': 0,
            'failed_parses': 0,
            'detailed_results': []
        }
        
        print(f"📋 Testing {len(test_cases)} date parsing cases...")
        
        for i, test_text in enumerate(test_cases):
            print(f"\n🔍 Test {i+1}: '{test_text}'")
            
            result = self.parse_posting_date(test_text)
            
            if result['success']:
                test_results['successful_parses'] += 1
                print(f"   ✅ Success: {result['parsed_datetime']} (confidence: {result['confidence_score']})")
                print(f"   📋 Pattern: {result['pattern_type']}")
            else:
                test_results['failed_parses'] += 1
                print(f"   ❌ Failed: {result['error']}")
            
            test_results['detailed_results'].append({
                'test_text': test_text,
                'result': result
            })
        
        # Calculate overall statistics
        stats = self.get_parsing_statistics()
        
        print(f"\n📊 DATE PARSING SYSTEM TEST RESULTS")
        print("="*50)
        print(f"✅ Test cases run: {test_results['test_cases_run']}")
        print(f"✅ Successful parses: {test_results['successful_parses']}")
        print(f"❌ Failed parses: {test_results['failed_parses']}")
        print(f"📈 Success rate: {stats['success_rate_percentage']}%")
        print(f"🔥 Most common pattern: {stats['most_common_pattern']}")
        
        test_results['statistics'] = stats
        
        return test_results


def main():
    """Main function for date parsing system testing"""
    
    try:
        date_parser = DateParsingSystem()
        test_results = date_parser.test_date_parsing_system()
        
        if test_results['successful_parses'] >= test_results['test_cases_run'] * 0.8:
            print("\n✅ Date parsing system test successful!")
            return True
        else:
            print("\n⚠️ Date parsing system needs improvement!")
            return False
            
    except Exception as e:
        print(f"❌ Date parsing system test failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
