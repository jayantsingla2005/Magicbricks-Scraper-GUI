#!/usr/bin/env python3
"""
Smart Stopping Logic Implementation
Implement conservative stopping when 80% of properties are older than last scrape date.
Based on evidence-based research findings.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
from pathlib import Path
from date_parsing_system import DateParsingSystem


class SmartStoppingLogic:
    """
    Smart stopping logic for incremental scraping with conservative thresholds
    """
    
    def __init__(self, db_path: str = 'magicbricks_enhanced.db'):
        """Initialize smart stopping logic"""
        
        self.db_path = db_path
        self.connection = None
        self.date_parser = DateParsingSystem(db_path)
        
        # Default stopping thresholds (evidence-based) - FIXED: Less aggressive
        self.stopping_config = {
            'old_property_threshold_percentage': 95,  # Stop when 95% are old (was 80%)
            'minimum_properties_per_page': 5,         # Need at least 5 properties to decide
            'maximum_pages_to_check': 100,            # Safety limit
            'date_buffer_hours': 2,                   # 2-hour buffer for safety
            'conservative_mode': False,               # More strict thresholds
            'require_consecutive_old_pages': 3,       # Need 3 consecutive old pages (was 2)
            'minimum_pages_before_stopping': 10      # Must scrape at least 10 pages
        }
        
        # Stopping statistics
        self.stopping_stats = {
            'pages_analyzed': 0,
            'properties_analyzed': 0,
            'old_properties_found': 0,
            'new_properties_found': 0,
            'stopping_decisions': [],
            'final_decision': None,
            'decision_confidence': 0.0
        }
        
        print("[STOP] Smart Stopping Logic Initialized")
    
    def connect_db(self):
        """Connect to database"""
        
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"[ERROR] Database connection failed: {str(e)}")
            return False
    
    def get_last_scrape_date(self, city: str, scrape_mode: str = 'incremental') -> Optional[datetime]:
        """Get the last successful scrape date for a city"""
        
        if not self.connect_db():
            return None
        
        try:
            cursor = self.connection.cursor()
            
            # Get the most recent successful scrape
            cursor.execute('''
                SELECT end_timestamp FROM scrape_sessions 
                WHERE city = ? AND status = 'completed' AND scrape_mode = ?
                ORDER BY end_timestamp DESC LIMIT 1
            ''', (city, scrape_mode))
            
            result = cursor.fetchone()
            
            if result:
                return datetime.fromisoformat(result[0])
            else:
                # If no previous incremental scrape, get last full scrape
                cursor.execute('''
                    SELECT end_timestamp FROM scrape_sessions 
                    WHERE city = ? AND status = 'completed' AND scrape_mode = 'full'
                    ORDER BY end_timestamp DESC LIMIT 1
                ''', (city,))
                
                result = cursor.fetchone()
                return datetime.fromisoformat(result[0]) if result else None
                
        except Exception as e:
            print(f"[ERROR] Error getting last scrape date: {str(e)}")
            return None
        
        finally:
            if self.connection:
                self.connection.close()
    
    def analyze_page_for_stopping(self, property_texts: List[str], last_scrape_date: datetime, 
                                 page_number: int, extraction_date: datetime = None) -> Dict[str, Any]:
        """Analyze a page of properties to determine if we should stop scraping"""
        
        if extraction_date is None:
            extraction_date = datetime.now()
        
        # Add buffer to last scrape date for safety
        buffered_last_scrape = last_scrape_date - timedelta(hours=self.stopping_config['date_buffer_hours'])
        
        page_analysis = {
            'page_number': page_number,
            'total_properties': len(property_texts),
            'properties_with_dates': 0,
            'old_properties': 0,
            'new_properties': 0,
            'old_percentage': 0.0,
            'should_stop': False,
            'stop_reason': None,
            'confidence': 0.0,
            'property_details': []
        }
        
        print(f"🔍 Analyzing page {page_number} with {len(property_texts)} properties...")
        
        # Check minimum properties requirement
        if len(property_texts) < self.stopping_config['minimum_properties_per_page']:
            page_analysis['should_stop'] = True
            page_analysis['stop_reason'] = f'Insufficient properties on page ({len(property_texts)} < {self.stopping_config["minimum_properties_per_page"]})'
            page_analysis['confidence'] = 0.9
            return page_analysis
        
        # Parse dates for all properties
        for i, property_text in enumerate(property_texts):
            parse_result = self.date_parser.parse_posting_date(property_text, extraction_date)
            
            property_detail = {
                'index': i,
                'text_sample': property_text[:100] + '...' if len(property_text) > 100 else property_text,
                'parse_result': parse_result,
                'is_old': False,
                'is_new': False
            }
            
            if parse_result['success'] and parse_result['parsed_datetime']:
                page_analysis['properties_with_dates'] += 1
                
                # Compare with buffered last scrape date
                if parse_result['parsed_datetime'] < buffered_last_scrape:
                    page_analysis['old_properties'] += 1
                    property_detail['is_old'] = True
                else:
                    page_analysis['new_properties'] += 1
                    property_detail['is_new'] = True
            
            page_analysis['property_details'].append(property_detail)
        
        # Calculate old percentage
        if page_analysis['properties_with_dates'] > 0:
            page_analysis['old_percentage'] = (page_analysis['old_properties'] / 
                                             page_analysis['properties_with_dates']) * 100
        
        # Determine if we should stop
        threshold = self.stopping_config['old_property_threshold_percentage']
        if self.stopping_config['conservative_mode']:
            threshold = 70  # More conservative threshold
        
        if page_analysis['old_percentage'] >= threshold:
            page_analysis['should_stop'] = True
            page_analysis['stop_reason'] = f'{page_analysis["old_percentage"]:.1f}% of properties are older than last scrape'
            page_analysis['confidence'] = min(0.9, page_analysis['old_percentage'] / 100)
        
        # Update statistics
        self.stopping_stats['pages_analyzed'] += 1
        self.stopping_stats['properties_analyzed'] += page_analysis['total_properties']
        self.stopping_stats['old_properties_found'] += page_analysis['old_properties']
        self.stopping_stats['new_properties_found'] += page_analysis['new_properties']
        self.stopping_stats['stopping_decisions'].append(page_analysis)
        
        print(f"   [STATS] Page {page_number}: {page_analysis['old_percentage']:.1f}% old properties")
        print(f"   [STOP] Should stop: {page_analysis['should_stop']}")
        
        return page_analysis
    
    def make_final_stopping_decision(self, page_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Make final decision based on multiple page analyses"""
        
        print("[TARGET] Making final stopping decision...")
        
        final_decision = {
            'should_stop_scraping': False,
            'stop_reason': None,
            'confidence': 0.0,
            'pages_analyzed': len(page_analyses),
            'total_properties': sum(p['total_properties'] for p in page_analyses),
            'overall_old_percentage': 0.0,
            'consecutive_old_pages': 0,
            'recommendation': ''
        }
        
        if not page_analyses:
            final_decision['stop_reason'] = 'No pages analyzed'
            final_decision['recommendation'] = 'Continue scraping - insufficient data'
            return final_decision
        
        # Calculate overall statistics
        total_old = sum(p['old_properties'] for p in page_analyses)
        total_new = sum(p['new_properties'] for p in page_analyses)
        total_with_dates = total_old + total_new
        
        if total_with_dates > 0:
            final_decision['overall_old_percentage'] = (total_old / total_with_dates) * 100
        
        # Count consecutive pages that suggest stopping
        consecutive_stop_pages = 0
        for analysis in reversed(page_analyses):  # Check from most recent
            if analysis['should_stop']:
                consecutive_stop_pages += 1
            else:
                break
        
        final_decision['consecutive_old_pages'] = consecutive_stop_pages
        
        # Decision logic - FIXED: Respect minimum pages requirement
        required_consecutive = self.stopping_config['require_consecutive_old_pages']
        minimum_pages = self.stopping_config.get('minimum_pages_before_stopping', 10)

        # Don't stop if we haven't scraped minimum pages
        if len(page_analyses) < minimum_pages:
            final_decision['recommendation'] = f'Continue scraping - only {len(page_analyses)}/{minimum_pages} minimum pages scraped'
        elif consecutive_stop_pages >= required_consecutive:
            final_decision['should_stop_scraping'] = True
            final_decision['stop_reason'] = f'{consecutive_stop_pages} consecutive pages with ≥95% old properties'
            final_decision['confidence'] = min(0.95, consecutive_stop_pages / required_consecutive * 0.8)
            final_decision['recommendation'] = 'Stop scraping - reached old property territory'
        
        elif final_decision['overall_old_percentage'] >= 90:
            final_decision['should_stop_scraping'] = True
            final_decision['stop_reason'] = f'Overall {final_decision["overall_old_percentage"]:.1f}% old properties'
            final_decision['confidence'] = 0.85
            final_decision['recommendation'] = 'Stop scraping - very high percentage of old properties'
        
        elif len(page_analyses) >= self.stopping_config['maximum_pages_to_check']:
            final_decision['should_stop_scraping'] = True
            final_decision['stop_reason'] = f'Reached maximum page limit ({self.stopping_config["maximum_pages_to_check"]})'
            final_decision['confidence'] = 0.7
            final_decision['recommendation'] = 'Stop scraping - safety limit reached'
        
        else:
            final_decision['recommendation'] = 'Continue scraping - not enough old properties found'
        
        # Update final statistics
        self.stopping_stats['final_decision'] = final_decision
        self.stopping_stats['decision_confidence'] = final_decision['confidence']
        
        print(f"   [TARGET] Final decision: {'STOP' if final_decision['should_stop_scraping'] else 'CONTINUE'}")
        print(f"   📊 Overall old percentage: {final_decision['overall_old_percentage']:.1f}%")
        print(f"   🔄 Consecutive old pages: {consecutive_stop_pages}")
        print(f"   💪 Confidence: {final_decision['confidence']:.2f}")
        
        return final_decision
    
    def save_stopping_analysis_to_db(self, session_id: int, page_analyses: List[Dict[str, Any]], 
                                   final_decision: Dict[str, Any]):
        """Save stopping analysis to database"""
        
        if not self.connect_db():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            print(f"[SAVE] Saving stopping analysis for session {session_id}...")
            
            # Save page-level statistics
            for analysis in page_analyses:
                cursor.execute('''
                    INSERT INTO scrape_statistics 
                    (session_id, page_number, properties_on_page, new_properties, 
                     oldest_property_date, newest_property_date, stop_decision, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    analysis['page_number'],
                    analysis['total_properties'],
                    analysis['new_properties'],
                    None,  # We could calculate this from property_details
                    None,  # We could calculate this from property_details
                    json.dumps({
                        'should_stop': analysis['should_stop'],
                        'stop_reason': analysis['stop_reason'],
                        'old_percentage': analysis['old_percentage'],
                        'confidence': analysis['confidence']
                    }),
                    datetime.now()
                ))
            
            # Update session with final decision
            cursor.execute('''
                UPDATE scrape_sessions 
                SET stop_reason = ?, configuration = ?
                WHERE session_id = ?
            ''', (
                final_decision['stop_reason'],
                json.dumps({
                    'stopping_config': self.stopping_config,
                    'final_decision': final_decision,
                    'stopping_stats': self.stopping_stats
                }),
                session_id
            ))
            
            self.connection.commit()
            print(f"[SUCCESS] Saved stopping analysis for session {session_id}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error saving stopping analysis: {str(e)}")
            self.connection.rollback()
            return False
        
        finally:
            if self.connection:
                self.connection.close()
    
    def test_smart_stopping_logic(self) -> Dict[str, Any]:
        """Test the smart stopping logic with simulated data"""
        
        print("🧪 TESTING SMART STOPPING LOGIC")
        print("="*50)
        
        # Simulate last scrape date (2 days ago)
        last_scrape_date = datetime.now() - timedelta(days=2)
        print(f"📅 Simulated last scrape date: {last_scrape_date}")
        
        # Test scenarios
        test_scenarios = [
            {
                'name': 'Mostly New Properties (should continue)',
                'property_texts': [
                    '5 hours ago Property 1',
                    '8 hours ago Property 2', 
                    '1 day ago Property 3',
                    '10 hours ago Property 4',
                    '6 hours ago Property 5'
                ]
            },
            {
                'name': 'Mixed Properties (should continue)',
                'property_texts': [
                    '1 day ago Property 1',
                    '3 days ago Property 2',
                    '5 hours ago Property 3',
                    '4 days ago Property 4',
                    '2 hours ago Property 5'
                ]
            },
            {
                'name': 'Mostly Old Properties (should stop)',
                'property_texts': [
                    '5 days ago Property 1',
                    '1 week ago Property 2',
                    '6 days ago Property 3',
                    '3 days ago Property 4',
                    '1 week ago Property 5'
                ]
            }
        ]
        
        test_results = {
            'scenarios_tested': len(test_scenarios),
            'correct_decisions': 0,
            'scenario_results': []
        }
        
        for i, scenario in enumerate(test_scenarios):
            print(f"\n🔍 Testing Scenario {i+1}: {scenario['name']}")
            
            # Analyze the page
            page_analysis = self.analyze_page_for_stopping(
                scenario['property_texts'], 
                last_scrape_date, 
                page_number=i+1
            )
            
            # Make decision based on single page (for testing)
            final_decision = self.make_final_stopping_decision([page_analysis])
            
            # Check if decision matches expectation
            expected_stop = 'should stop' in scenario['name'].lower()
            actual_stop = final_decision['should_stop_scraping']
            correct_decision = expected_stop == actual_stop
            
            if correct_decision:
                test_results['correct_decisions'] += 1
            
            scenario_result = {
                'scenario': scenario['name'],
                'expected_stop': expected_stop,
                'actual_stop': actual_stop,
                'correct_decision': correct_decision,
                'old_percentage': page_analysis['old_percentage'],
                'confidence': final_decision['confidence']
            }
            
            test_results['scenario_results'].append(scenario_result)
            
            print(f"   [STATS] Old percentage: {page_analysis['old_percentage']:.1f}%")
            print(f"   [DECISION] Decision: {'STOP' if actual_stop else 'CONTINUE'}")
            print(f"   [RESULT] Correct: {correct_decision}")
        
        # Calculate overall test success
        success_rate = (test_results['correct_decisions'] / test_results['scenarios_tested']) * 100
        
        print(f"\n[STATS] SMART STOPPING LOGIC TEST RESULTS")
        print("="*50)
        print(f"[SUCCESS] Scenarios tested: {test_results['scenarios_tested']}")
        print(f"[SUCCESS] Correct decisions: {test_results['correct_decisions']}")
        print(f"[RATE] Success rate: {success_rate:.1f}%")
        
        test_results['success_rate'] = success_rate
        
        return test_results


def main():
    """Main function for smart stopping logic testing"""
    
    try:
        stopping_logic = SmartStoppingLogic()
        test_results = stopping_logic.test_smart_stopping_logic()
        
        if test_results['success_rate'] >= 80:
            print("\n[SUCCESS] Smart stopping logic test successful!")
            return True
        else:
            print("\n[WARNING] Smart stopping logic needs improvement!")
            return False
            
    except Exception as e:
        print(f"[ERROR] Smart stopping logic test failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
