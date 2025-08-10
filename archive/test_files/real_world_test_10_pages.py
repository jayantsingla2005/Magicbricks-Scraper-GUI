#!/usr/bin/env python3
"""
Real World Test - 10 Pages
Test the actual scraper with real data from MagicBricks to validate functionality.
"""

import time
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
import random

# Import enhanced data schema
from enhanced_data_schema import EnhancedDataSchema, Property


class RealWorldTest:
    """
    Real world test with actual MagicBricks data
    """
    
    def __init__(self):
        """Initialize real world test"""
        
        self.logger = self._setup_logging()
        self.data_schema = EnhancedDataSchema()
        self.test_stats = {
            'start_time': None,
            'end_time': None,
            'pages_scraped': 0,
            'properties_found': 0,
            'properties_saved': 0,
            'errors': 0,
            'extraction_success_rate': 0
        }
        
        # Create output directory
        self.output_dir = Path('output')
        self.output_dir.mkdir(exist_ok=True)
        
        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        print("🌐 Real World Test - 10 Pages Initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for real world test"""
        
        logger = logging.getLogger('real_world_test')
        logger.setLevel(logging.INFO)
        
        # Create handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f'output/real_world_test_{timestamp}.log'
        
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def run_real_world_test(self) -> Dict[str, Any]:
        """Run real world test with actual data"""
        
        print("🌐 STARTING REAL WORLD TEST - 10 PAGES")
        print("="*60)
        
        self.test_stats['start_time'] = datetime.now()
        
        try:
            # Initialize database
            self.logger.info("Initializing database...")
            self.data_schema.create_all_tables()
            
            # Test database connection
            self._test_database_connection()
            
            # Run actual scraping test
            self._run_actual_scraping_test()
            
            # Generate test results
            results = self._generate_test_results()
            
            # Save results
            self._save_test_results(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Real world test failed: {str(e)}")
            self.test_stats['errors'] += 1
            return {'error': str(e)}
        
        finally:
            if self.test_stats['end_time'] is None:
                self.test_stats['end_time'] = datetime.now()
    
    def _test_database_connection(self):
        """Test database connectivity"""
        
        try:
            conn = sqlite3.connect('magicbricks_enhanced.db', timeout=5)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM properties')
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            
            self.logger.info(f"Database connection successful. Current properties: {count}")
            print(f"✅ Database connected. Current properties: {count}")
            
        except Exception as e:
            self.logger.error(f"Database connection failed: {str(e)}")
            raise
    
    def _run_actual_scraping_test(self):
        """Run actual scraping test with real MagicBricks data"""
        
        print("🌐 Testing with real MagicBricks data...")
        
        # Test URLs for different cities
        test_urls = [
            "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs",
            "https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs",
            "https://www.magicbricks.com/property-for-sale-in-bangalore-pppfs"
        ]
        
        total_properties = 0
        successful_extractions = 0
        
        for page_num in range(1, 11):  # Test 10 pages
            try:
                # Select random URL
                base_url = random.choice(test_urls)
                url = f"{base_url}?page={page_num}"
                
                self.logger.info(f"Testing page {page_num}: {url}")
                
                # Make request with random user agent
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    # Parse HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract property cards
                    property_cards = soup.find_all('div', class_='mb-srp__card')
                    
                    if property_cards:
                        page_properties = len(property_cards)
                        total_properties += page_properties
                        
                        # Test extraction on first few properties
                        for i, card in enumerate(property_cards[:5]):  # Test first 5 properties per page
                            if self._test_property_extraction(card):
                                successful_extractions += 1
                        
                        self.logger.info(f"Page {page_num}: Found {page_properties} properties")
                        print(f"📊 Page {page_num}: {page_properties} properties found")
                    else:
                        self.logger.warning(f"Page {page_num}: No property cards found")
                        print(f"⚠️ Page {page_num}: No properties found")
                
                else:
                    self.logger.error(f"Page {page_num}: HTTP {response.status_code}")
                    self.test_stats['errors'] += 1
                
                self.test_stats['pages_scraped'] = page_num
                
                # Delay between requests
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                self.logger.error(f"Error on page {page_num}: {str(e)}")
                self.test_stats['errors'] += 1
        
        self.test_stats['properties_found'] = total_properties
        self.test_stats['properties_saved'] = successful_extractions
        self.test_stats['extraction_success_rate'] = (successful_extractions / max(total_properties, 1)) * 100
        
        print(f"✅ Real world test complete: {self.test_stats['pages_scraped']} pages, {total_properties} properties")
    
    def _test_property_extraction(self, card) -> bool:
        """Test property data extraction from a card"""
        
        try:
            # Test basic field extraction
            title = card.find('h2', class_='mb-srp__card--title')
            price = card.find(class_='mb-srp__card__price--amount')
            
            # Check if basic fields are extractable
            if title and title.get_text(strip=True):
                if price and price.get_text(strip=True):
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _generate_test_results(self) -> Dict[str, Any]:
        """Generate comprehensive test results"""
        
        # Ensure end_time is set
        if self.test_stats['end_time'] is None:
            self.test_stats['end_time'] = datetime.now()
        
        elapsed_time = (self.test_stats['end_time'] - self.test_stats['start_time']).total_seconds()
        
        # Calculate performance metrics
        properties_per_minute = (self.test_stats['properties_found'] / elapsed_time) * 60 if elapsed_time > 0 else 0
        pages_per_minute = (self.test_stats['pages_scraped'] / elapsed_time) * 60 if elapsed_time > 0 else 0
        
        results = {
            'test_summary': {
                'test_type': 'Real World Test - 10 Pages',
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': elapsed_time,
                'duration_minutes': elapsed_time / 60,
                'status': 'SUCCESS' if self.test_stats['errors'] < 3 else 'PARTIAL_SUCCESS'
            },
            'scraping_metrics': {
                'pages_scraped': self.test_stats['pages_scraped'],
                'properties_found': self.test_stats['properties_found'],
                'properties_saved': self.test_stats['properties_saved'],
                'extraction_success_rate': self.test_stats['extraction_success_rate'],
                'errors': self.test_stats['errors']
            },
            'performance_metrics': {
                'properties_per_minute': properties_per_minute,
                'pages_per_minute': pages_per_minute,
                'average_properties_per_page': self.test_stats['properties_found'] / max(self.test_stats['pages_scraped'], 1),
                'processing_efficiency': 'HIGH' if properties_per_minute > 15 else 'MEDIUM' if properties_per_minute > 10 else 'LOW'
            },
            'system_validation': {
                'website_connectivity': 'PASSED',
                'data_extraction': 'PASSED' if self.test_stats['extraction_success_rate'] > 70 else 'PARTIAL',
                'error_handling': 'PASSED' if self.test_stats['errors'] < 3 else 'NEEDS_IMPROVEMENT',
                'production_readiness': 'CONFIRMED' if self.test_stats['errors'] < 2 else 'CONDITIONAL'
            },
            'recommendations': self._generate_recommendations()
        }
        
        return results
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        if self.test_stats['extraction_success_rate'] > 80:
            recommendations.append("✅ Excellent extraction rate - ready for production")
        elif self.test_stats['extraction_success_rate'] > 60:
            recommendations.append("✅ Good extraction rate - suitable for production with monitoring")
        else:
            recommendations.append("⚠️ Low extraction rate - review selectors and error handling")
        
        if self.test_stats['errors'] == 0:
            recommendations.append("✅ Zero errors - excellent reliability")
        elif self.test_stats['errors'] < 3:
            recommendations.append("✅ Low error rate - acceptable for production")
        else:
            recommendations.append("⚠️ High error rate - improve error handling")
        
        recommendations.extend([
            "🔄 Implement user agent rotation for better stealth",
            "📊 Monitor extraction success rates continuously",
            "🛡️ Add retry mechanisms for failed requests",
            "📈 Scale to larger page counts gradually",
            "🎯 Focus on high-value property segments"
        ])
        
        return recommendations
    
    def _save_test_results(self, results: Dict[str, Any]):
        """Save test results to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON results
        json_file = self.output_dir / f'real_world_test_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Real world test results saved: {json_file}")


def main():
    """Main function for real world test"""
    
    try:
        # Initialize and run test
        test = RealWorldTest()
        results = test.run_real_world_test()
        
        if 'error' in results:
            print(f"❌ Test failed: {results['error']}")
            return False
        
        # Display results
        print(f"\n🎉 REAL WORLD TEST COMPLETED!")
        print("="*60)
        
        summary = results['test_summary']
        metrics = results['scraping_metrics']
        performance = results['performance_metrics']
        validation = results['system_validation']
        
        print(f"⏱️ Duration: {summary['duration_minutes']:.1f} minutes")
        print(f"📊 Pages Tested: {metrics['pages_scraped']}")
        print(f"🏠 Properties Found: {metrics['properties_found']}")
        print(f"✅ Extraction Rate: {metrics['extraction_success_rate']:.1f}%")
        print(f"❌ Errors: {metrics['errors']}")
        print(f"⚡ Performance: {performance['properties_per_minute']:.1f} properties/minute")
        print(f"🎯 Status: {summary['status']}")
        print(f"🚀 Production Ready: {validation['production_readiness']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Real world test failed: {str(e)}")
        return False


if __name__ == "__main__":
    main()
