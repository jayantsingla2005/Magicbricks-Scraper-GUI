#!/usr/bin/env python3
"""
Edge Case Discovery & Analysis Tool
Identifies and analyzes edge cases, boundary conditions, and unusual data formats
across MagicBricks platform to ensure robust extraction handling.
"""

import time
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import statistics

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# BeautifulSoup for parsing
from bs4 import BeautifulSoup, Tag


class EdgeCaseDiscoveryAnalyzer:
    """
    Comprehensive analyzer for edge cases and boundary conditions
    """
    
    def __init__(self):
        """Initialize edge case discovery analyzer"""
        
        # Edge case categories to analyze
        self.edge_case_categories = {
            'price_edge_cases': {
                'patterns': [
                    r'price\s*on\s*request',
                    r'contact\s*for\s*price',
                    r'negotiable',
                    r'₹\s*0',
                    r'starting\s*from',
                    r'onwards',
                    r'under\s*construction',
                    r'ready\s*to\s*move',
                    r'₹\s*\d+\s*-\s*₹\s*\d+',  # Price ranges
                    r'₹\s*\d+\.\d+\s*-\s*\d+\.\d+',  # Decimal ranges
                    r'emi\s*starts\s*from',
                    r'all\s*inclusive'
                ],
                'description': 'Unusual price formats and edge cases'
            },
            'area_edge_cases': {
                'patterns': [
                    r'\d+\s*-\s*\d+\s*sqft',  # Area ranges
                    r'approx\s*\d+\s*sqft',
                    r'upto\s*\d+\s*sqft',
                    r'from\s*\d+\s*sqft',
                    r'\d+\s*sqft\s*onwards',
                    r'\d+\s*sqft\s*\+',
                    r'variable\s*sizes',
                    r'customizable',
                    r'\d+\s*sq\s*(?!ft|yards|m)',  # Incomplete units
                    r'\d+\s*square',  # Incomplete square
                    r'plot\s*size:\s*\d+\s*x\s*\d+'  # Dimensional format
                ],
                'description': 'Unusual area formats and boundary conditions'
            },
            'property_type_edge_cases': {
                'patterns': [
                    r'studio\s*apartment',
                    r'service\s*apartment',
                    r'penthouse',
                    r'duplex',
                    r'triplex',
                    r'row\s*house',
                    r'twin\s*house',
                    r'cluster\s*home',
                    r'farmhouse',
                    r'weekend\s*home',
                    r'commercial\s*cum\s*residential',
                    r'mixed\s*use',
                    r'under\s*construction',
                    r'pre\s*launch',
                    r'ready\s*possession'
                ],
                'description': 'Unusual property types and status combinations'
            },
            'location_edge_cases': {
                'patterns': [
                    r'near\s*metro',
                    r'highway\s*facing',
                    r'corner\s*plot',
                    r'main\s*road',
                    r'internal\s*road',
                    r'gated\s*community',
                    r'society\s*name\s*not\s*disclosed',
                    r'project\s*name\s*withheld',
                    r'prime\s*location',
                    r'upcoming\s*area',
                    r'developing\s*locality',
                    r'established\s*neighborhood'
                ],
                'description': 'Unusual location descriptions and formats'
            },
            'configuration_edge_cases': {
                'patterns': [
                    r'\d+\.\d+\s*bhk',  # Fractional BHK
                    r'\d+\s*rk',  # Room-Kitchen format
                    r'\d+\s*bhk\s*\+\s*study',
                    r'\d+\s*bhk\s*\+\s*servant',
                    r'\d+\s*bhk\s*duplex',
                    r'\d+\s*bhk\s*triplex',
                    r'studio',
                    r'loft',
                    r'\d+\s*bed\s*\+\s*den',
                    r'convertible\s*\d+\s*bhk',
                    r'flexible\s*layout'
                ],
                'description': 'Unusual property configurations'
            },
            'data_format_edge_cases': {
                'patterns': [
                    r'[^\x00-\x7F]+',  # Non-ASCII characters
                    r'\d+\s*[^\w\s]+\s*\d+',  # Special characters in numbers
                    r'₹\s*[^\d\s]',  # Currency with non-numeric
                    r'\d+\s*,\s*\d+\s*,\s*\d+',  # Multiple commas
                    r'\d+\.\d+\.\d+',  # Multiple decimals
                    r'\s{3,}',  # Excessive whitespace
                    r'[A-Z]{3,}',  # All caps text
                    r'\d+[a-zA-Z]+\d+',  # Mixed alphanumeric
                    r'[^\w\s₹.,()-]+'  # Unusual special characters
                ],
                'description': 'Unusual data formatting and encoding issues'
            }
        }
        
        # Analysis results
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'pages_analyzed': 0,
            'properties_analyzed': 0,
            'edge_cases_discovered': {},
            'frequency_analysis': {},
            'impact_assessment': {},
            'handling_strategies': {},
            'robustness_recommendations': []
        }
        
        # Test URLs for comprehensive edge case discovery
        self.test_urls = [
            'https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs',
            'https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs',
            'https://www.magicbricks.com/property-for-sale-in-bangalore-pppfs',
            'https://www.magicbricks.com/property-for-sale-in-delhi-pppfs'
        ]
        
        print("🔍 Edge Case Discovery & Analysis Tool Initialized")
        print(f"🎯 Analyzing {len(self.edge_case_categories)} edge case categories")
        print(f"📊 Target URLs: {len(self.test_urls)}")
    
    def discover_and_analyze_edge_cases(self) -> Dict[str, Any]:
        """
        Perform comprehensive edge case discovery and analysis
        """
        
        print("\n🚀 Starting Edge Case Discovery & Analysis")
        print("="*60)
        
        try:
            # Step 1: Discover edge cases across multiple sources
            print("🔍 Step 1: Discovering Edge Cases Across Multiple Sources...")
            edge_case_data = self._discover_edge_cases()
            
            if not edge_case_data:
                print("❌ No edge case data could be discovered")
                return self.analysis_results
            
            # Step 2: Analyze edge case patterns
            print("\n📊 Step 2: Analyzing Edge Case Patterns...")
            self._analyze_edge_case_patterns(edge_case_data)
            
            # Step 3: Assess frequency and impact
            print("\n📈 Step 3: Assessing Frequency and Impact...")
            self._assess_frequency_and_impact(edge_case_data)
            
            # Step 4: Evaluate current handling capabilities
            print("\n🧪 Step 4: Evaluating Current Handling Capabilities...")
            self._evaluate_current_handling(edge_case_data)
            
            # Step 5: Develop handling strategies
            print("\n⚡ Step 5: Developing Handling Strategies...")
            self._develop_handling_strategies()
            
            # Step 6: Generate robustness recommendations
            print("\n💡 Step 6: Generating Robustness Recommendations...")
            self._generate_robustness_recommendations()
            
            # Step 7: Save analysis results
            print("\n💾 Step 7: Saving Analysis Results...")
            self._save_analysis_results()
            
            print("\n✅ Edge Case Discovery & Analysis Complete!")
            self._print_analysis_summary()
            
            return self.analysis_results
            
        except Exception as e:
            print(f"❌ Edge case discovery and analysis failed: {str(e)}")
            self.analysis_results['error'] = str(e)
            return self.analysis_results
    
    def _discover_edge_cases(self) -> List[Dict[str, Any]]:
        """Discover edge cases from multiple sources"""
        
        all_edge_case_data = []
        
        for i, url in enumerate(self.test_urls, 1):
            print(f"🔍 Discovering from source {i}/{len(self.test_urls)}...")
            
            try:
                source_data = self._discover_from_single_source(url)
                if source_data:
                    all_edge_case_data.extend(source_data)
                    print(f"✅ Source {i}: Discovered {len(source_data)} property data points")
                else:
                    print(f"⚠️ Source {i}: No data discovered")
                
                # Delay between sources
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ Source {i}: Discovery failed - {str(e)}")
        
        self.analysis_results['pages_analyzed'] = len(self.test_urls)
        self.analysis_results['properties_analyzed'] = len(all_edge_case_data)
        
        return all_edge_case_data
    
    def _discover_from_single_source(self, url: str) -> List[Dict[str, Any]]:
        """Discover edge cases from a single source"""
        
        driver = self._setup_browser()
        
        try:
            # Navigate to page
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)
            
            # Parse page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find property cards
            property_cards = soup.select('.mb-srp__card')
            
            source_data = []
            
            for i, card in enumerate(property_cards[:30]):  # Analyze first 30 properties
                try:
                    property_data = self._analyze_card_for_edge_cases(card, i)
                    if property_data:
                        property_data['source_url'] = url
                        source_data.append(property_data)
                
                except Exception as e:
                    print(f"   ⚠️ Error analyzing card {i}: {str(e)}")
            
            return source_data
            
        finally:
            driver.quit()
    
    def _analyze_card_for_edge_cases(self, card: Tag, card_index: int) -> Optional[Dict[str, Any]]:
        """Analyze a property card for edge cases"""
        
        try:
            # Get all text content from the card
            card_text = card.get_text()
            
            # Initialize property data
            property_data = {
                'card_index': card_index,
                'raw_text': card_text,
                'edge_cases_found': {},
                'total_edge_cases': 0,
                'severity_assessment': 'low'
            }
            
            # Check each edge case category
            for category, config in self.edge_case_categories.items():
                category_matches = []
                
                for pattern in config['patterns']:
                    matches = re.findall(pattern, card_text, re.IGNORECASE)
                    
                    if matches:
                        for match in matches:
                            category_matches.append({
                                'pattern': pattern,
                                'match': match if isinstance(match, str) else str(match),
                                'full_context': self._extract_context(card_text, pattern)
                            })
                
                if category_matches:
                    property_data['edge_cases_found'][category] = category_matches
                    property_data['total_edge_cases'] += len(category_matches)
            
            # Assess severity
            property_data['severity_assessment'] = self._assess_edge_case_severity(property_data)
            
            return property_data
            
        except Exception as e:
            return None
    
    def _extract_context(self, text: str, pattern: str) -> str:
        """Extract context around a pattern match"""
        
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                return text[start:end].strip()
            return ""
        except Exception:
            return ""
    
    def _assess_edge_case_severity(self, property_data: Dict[str, Any]) -> str:
        """Assess the severity of edge cases in a property"""
        
        total_cases = property_data['total_edge_cases']
        
        # Check for critical edge cases
        critical_categories = ['price_edge_cases', 'area_edge_cases']
        critical_cases = sum(
            len(property_data['edge_cases_found'].get(cat, []))
            for cat in critical_categories
        )
        
        if critical_cases >= 3:
            return 'high'
        elif total_cases >= 5:
            return 'medium'
        elif total_cases >= 2:
            return 'low'
        else:
            return 'minimal'
    
    def _analyze_edge_case_patterns(self, edge_case_data: List[Dict[str, Any]]):
        """Analyze patterns in discovered edge cases"""
        
        print("📊 Analyzing edge case patterns...")
        
        patterns_discovered = {}
        
        for category in self.edge_case_categories.keys():
            category_patterns = defaultdict(int)
            category_contexts = defaultdict(list)
            
            for property_data in edge_case_data:
                edge_cases = property_data.get('edge_cases_found', {}).get(category, [])
                
                for edge_case in edge_cases:
                    pattern = edge_case['pattern']
                    match = edge_case['match']
                    context = edge_case['full_context']
                    
                    category_patterns[pattern] += 1
                    category_contexts[pattern].append({
                        'match': match,
                        'context': context[:100]  # First 100 chars
                    })
            
            patterns_discovered[category] = {
                'pattern_frequencies': dict(category_patterns),
                'pattern_contexts': dict(category_contexts),
                'total_patterns': len(category_patterns),
                'total_occurrences': sum(category_patterns.values())
            }
        
        self.analysis_results['edge_cases_discovered'] = patterns_discovered
    
    def _assess_frequency_and_impact(self, edge_case_data: List[Dict[str, Any]]):
        """Assess frequency and impact of edge cases"""
        
        print("📈 Assessing frequency and impact...")
        
        frequency_analysis = {}
        
        # Overall frequency analysis
        total_properties = len(edge_case_data)
        properties_with_edge_cases = sum(1 for prop in edge_case_data if prop['total_edge_cases'] > 0)
        
        # Severity distribution
        severity_distribution = defaultdict(int)
        for property_data in edge_case_data:
            severity = property_data['severity_assessment']
            severity_distribution[severity] += 1
        
        # Category impact analysis
        category_impact = {}
        for category in self.edge_case_categories.keys():
            properties_affected = sum(
                1 for prop in edge_case_data 
                if category in prop.get('edge_cases_found', {})
            )
            
            impact_percentage = (properties_affected / total_properties * 100) if total_properties > 0 else 0
            
            category_impact[category] = {
                'properties_affected': properties_affected,
                'impact_percentage': impact_percentage,
                'severity': 'high' if impact_percentage > 20 else 'medium' if impact_percentage > 10 else 'low'
            }
        
        frequency_analysis = {
            'total_properties_analyzed': total_properties,
            'properties_with_edge_cases': properties_with_edge_cases,
            'edge_case_prevalence': (properties_with_edge_cases / total_properties * 100) if total_properties > 0 else 0,
            'severity_distribution': dict(severity_distribution),
            'category_impact': category_impact
        }
        
        self.analysis_results['frequency_analysis'] = frequency_analysis
    
    def _evaluate_current_handling(self, edge_case_data: List[Dict[str, Any]]):
        """Evaluate current handling capabilities for edge cases"""
        
        print("🧪 Evaluating current handling capabilities...")
        
        # Simulate current extraction on edge cases
        handling_evaluation = {}
        
        for category in self.edge_case_categories.keys():
            category_evaluation = {
                'total_cases': 0,
                'likely_handled': 0,
                'likely_failed': 0,
                'handling_rate': 0,
                'failure_examples': []
            }
            
            for property_data in edge_case_data:
                edge_cases = property_data.get('edge_cases_found', {}).get(category, [])
                
                for edge_case in edge_cases:
                    category_evaluation['total_cases'] += 1
                    
                    # Assess if current selectors would handle this case
                    if self._would_current_selectors_handle(category, edge_case):
                        category_evaluation['likely_handled'] += 1
                    else:
                        category_evaluation['likely_failed'] += 1
                        
                        if len(category_evaluation['failure_examples']) < 5:
                            category_evaluation['failure_examples'].append({
                                'pattern': edge_case['pattern'],
                                'match': edge_case['match'],
                                'context': edge_case['full_context'][:100]
                            })
            
            if category_evaluation['total_cases'] > 0:
                category_evaluation['handling_rate'] = (
                    category_evaluation['likely_handled'] / category_evaluation['total_cases'] * 100
                )
            
            handling_evaluation[category] = category_evaluation
        
        self.analysis_results['impact_assessment'] = handling_evaluation
    
    def _would_current_selectors_handle(self, category: str, edge_case: Dict[str, Any]) -> bool:
        """Assess if current selectors would handle an edge case"""
        
        pattern = edge_case['pattern']
        match = edge_case['match']
        
        # Simple heuristics for current selector capabilities
        if category == 'price_edge_cases':
            # Current selectors likely handle standard ₹ patterns
            if '₹' in match and any(unit in match.lower() for unit in ['lac', 'cr', 'lakh', 'crore']):
                return True
            # But likely fail on "price on request", "negotiable", etc.
            if any(term in match.lower() for term in ['request', 'negotiable', 'contact']):
                return False
        
        elif category == 'area_edge_cases':
            # Current selectors likely handle standard sqft patterns
            if 'sqft' in match.lower() and re.search(r'\d+', match):
                return True
            # But likely fail on ranges, approximations
            if any(term in match.lower() for term in ['approx', 'upto', 'from', 'onwards', '-']):
                return False
        
        elif category == 'configuration_edge_cases':
            # Current selectors likely handle standard BHK
            if re.search(r'\d+\s*bhk', match.lower()):
                return True
            # But likely fail on fractional, RK, studio
            if any(term in match.lower() for term in ['rk', 'studio', 'loft', '.']):
                return False
        
        # Default: assume current selectors have limited edge case handling
        return False
    
    def _develop_handling_strategies(self):
        """Develop strategies for handling discovered edge cases"""
        
        print("⚡ Developing handling strategies...")
        
        strategies = {}
        
        for category, analysis in self.analysis_results.get('edge_cases_discovered', {}).items():
            category_strategies = []
            
            # Get most common patterns for this category
            pattern_frequencies = analysis.get('pattern_frequencies', {})
            top_patterns = sorted(pattern_frequencies.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for pattern, frequency in top_patterns:
                if frequency >= 3:  # Focus on patterns occurring 3+ times
                    strategy = self._develop_pattern_strategy(category, pattern, frequency)
                    if strategy:
                        category_strategies.append(strategy)
            
            strategies[category] = category_strategies
        
        self.analysis_results['handling_strategies'] = strategies
    
    def _develop_pattern_strategy(self, category: str, pattern: str, frequency: int) -> Optional[Dict[str, Any]]:
        """Develop strategy for handling a specific pattern"""
        
        strategy = {
            'pattern': pattern,
            'frequency': frequency,
            'category': category,
            'handling_approach': None,
            'implementation_priority': 'low',
            'fallback_value': None
        }
        
        if category == 'price_edge_cases':
            if 'request' in pattern or 'contact' in pattern:
                strategy.update({
                    'handling_approach': 'set_null_with_flag',
                    'implementation_priority': 'high',
                    'fallback_value': None,
                    'additional_field': 'price_on_request'
                })
            elif 'negotiable' in pattern:
                strategy.update({
                    'handling_approach': 'extract_base_price_if_available',
                    'implementation_priority': 'medium',
                    'fallback_value': None,
                    'additional_field': 'price_negotiable'
                })
            elif 'onwards' in pattern or 'starting' in pattern:
                strategy.update({
                    'handling_approach': 'extract_starting_price',
                    'implementation_priority': 'high',
                    'fallback_value': None,
                    'additional_field': 'price_type'
                })
        
        elif category == 'area_edge_cases':
            if 'approx' in pattern:
                strategy.update({
                    'handling_approach': 'extract_approximate_value',
                    'implementation_priority': 'medium',
                    'fallback_value': None,
                    'additional_field': 'area_approximate'
                })
            elif '-' in pattern:  # Range pattern
                strategy.update({
                    'handling_approach': 'extract_range_values',
                    'implementation_priority': 'high',
                    'fallback_value': None,
                    'additional_field': 'area_range'
                })
        
        elif category == 'configuration_edge_cases':
            if 'studio' in pattern:
                strategy.update({
                    'handling_approach': 'set_studio_configuration',
                    'implementation_priority': 'high',
                    'fallback_value': '0 BHK',
                    'additional_field': 'property_subtype'
                })
            elif 'rk' in pattern:
                strategy.update({
                    'handling_approach': 'convert_rk_to_bhk',
                    'implementation_priority': 'medium',
                    'fallback_value': None,
                    'additional_field': 'original_configuration'
                })
        
        return strategy if strategy['handling_approach'] else None
    
    def _generate_robustness_recommendations(self):
        """Generate recommendations for improving robustness"""
        
        print("💡 Generating robustness recommendations...")
        
        recommendations = []
        
        # Analyze overall edge case prevalence
        frequency_analysis = self.analysis_results.get('frequency_analysis', {})
        edge_case_prevalence = frequency_analysis.get('edge_case_prevalence', 0)
        
        if edge_case_prevalence > 30:
            recommendations.append({
                'priority': 'high',
                'category': 'overall_robustness',
                'recommendation': f"High edge case prevalence ({edge_case_prevalence:.1f}%). Implement comprehensive edge case handling framework.",
                'action': 'implement_edge_case_framework'
            })
        elif edge_case_prevalence > 15:
            recommendations.append({
                'priority': 'medium',
                'category': 'overall_robustness',
                'recommendation': f"Moderate edge case prevalence ({edge_case_prevalence:.1f}%). Focus on high-impact categories.",
                'action': 'targeted_edge_case_handling'
            })
        
        # Category-specific recommendations
        category_impact = frequency_analysis.get('category_impact', {})
        
        for category, impact_data in category_impact.items():
            impact_percentage = impact_data.get('impact_percentage', 0)
            
            if impact_percentage > 20:
                recommendations.append({
                    'priority': 'high',
                    'category': category,
                    'recommendation': f"{category.replace('_', ' ').title()} affects {impact_percentage:.1f}% of properties. Requires immediate attention.",
                    'action': 'implement_category_specific_handling',
                    'impact_percentage': impact_percentage
                })
            elif impact_percentage > 10:
                recommendations.append({
                    'priority': 'medium',
                    'category': category,
                    'recommendation': f"{category.replace('_', ' ').title()} affects {impact_percentage:.1f}% of properties. Consider enhanced handling.",
                    'action': 'enhance_category_handling',
                    'impact_percentage': impact_percentage
                })
        
        # Handling capability recommendations
        impact_assessment = self.analysis_results.get('impact_assessment', {})
        
        for category, evaluation in impact_assessment.items():
            handling_rate = evaluation.get('handling_rate', 0)
            
            if handling_rate < 50:
                recommendations.append({
                    'priority': 'high',
                    'category': category,
                    'recommendation': f"Low handling rate ({handling_rate:.1f}%) for {category.replace('_', ' ')}. Significant improvement needed.",
                    'action': 'redesign_extraction_logic',
                    'current_handling_rate': handling_rate
                })
            elif handling_rate < 75:
                recommendations.append({
                    'priority': 'medium',
                    'category': category,
                    'recommendation': f"Moderate handling rate ({handling_rate:.1f}%) for {category.replace('_', ' ')}. Room for improvement.",
                    'action': 'optimize_extraction_patterns',
                    'current_handling_rate': handling_rate
                })
        
        # Implementation recommendations
        strategies = self.analysis_results.get('handling_strategies', {})
        high_priority_strategies = 0
        
        for category_strategies in strategies.values():
            high_priority_strategies += len([s for s in category_strategies if s.get('implementation_priority') == 'high'])
        
        if high_priority_strategies > 5:
            recommendations.append({
                'priority': 'high',
                'category': 'implementation',
                'recommendation': f"{high_priority_strategies} high-priority edge case patterns identified. Implement in phases.",
                'action': 'phased_implementation_plan'
            })
        
        self.analysis_results['robustness_recommendations'] = recommendations
    
    def _save_analysis_results(self):
        """Save analysis results to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"edge_case_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📁 Analysis results saved: {filename}")
        
        # Save summary report
        summary_filename = f"edge_case_summary_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("EDGE CASE DISCOVERY & ANALYSIS SUMMARY\n")
            f.write("="*50 + "\n\n")
            
            f.write(f"Pages Analyzed: {self.analysis_results['pages_analyzed']}\n")
            f.write(f"Properties Analyzed: {self.analysis_results['properties_analyzed']}\n\n")
            
            # Frequency analysis
            frequency_data = self.analysis_results.get('frequency_analysis', {})
            f.write("EDGE CASE PREVALENCE:\n")
            f.write("-" * 25 + "\n")
            f.write(f"Properties with Edge Cases: {frequency_data.get('properties_with_edge_cases', 0)}\n")
            f.write(f"Edge Case Prevalence: {frequency_data.get('edge_case_prevalence', 0):.1f}%\n\n")
            
            # Category impact
            category_impact = frequency_data.get('category_impact', {})
            f.write("CATEGORY IMPACT:\n")
            f.write("-" * 25 + "\n")
            for category, impact in sorted(category_impact.items(), key=lambda x: x[1]['impact_percentage'], reverse=True):
                f.write(f"{category.replace('_', ' ').title()}: {impact['impact_percentage']:.1f}% impact\n")
            
            # Top recommendations
            f.write("\nTOP RECOMMENDATIONS:\n")
            f.write("-" * 25 + "\n")
            recommendations = self.analysis_results.get('robustness_recommendations', [])
            high_priority = [r for r in recommendations if r.get('priority') == 'high']
            for i, rec in enumerate(high_priority[:5], 1):
                f.write(f"{i}. {rec['recommendation']}\n")
        
        print(f"📄 Summary report saved: {summary_filename}")
    
    def _print_analysis_summary(self):
        """Print comprehensive analysis summary"""
        
        print("\n📊 EDGE CASE DISCOVERY & ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"📄 Pages Analyzed: {self.analysis_results['pages_analyzed']}")
        print(f"🏠 Properties Analyzed: {self.analysis_results['properties_analyzed']}")
        
        # Edge case prevalence
        frequency_data = self.analysis_results.get('frequency_analysis', {})
        edge_case_prevalence = frequency_data.get('edge_case_prevalence', 0)
        properties_with_edge_cases = frequency_data.get('properties_with_edge_cases', 0)
        
        print(f"\n🔍 EDGE CASE PREVALENCE:")
        print(f"   📊 Properties with Edge Cases: {properties_with_edge_cases}")
        print(f"   📈 Edge Case Prevalence: {edge_case_prevalence:.1f}%")
        
        # Severity distribution
        severity_dist = frequency_data.get('severity_distribution', {})
        if severity_dist:
            print(f"\n⚠️ SEVERITY DISTRIBUTION:")
            for severity, count in sorted(severity_dist.items(), key=lambda x: x[1], reverse=True):
                print(f"   {severity.upper()}: {count} properties")
        
        # Category impact
        category_impact = frequency_data.get('category_impact', {})
        if category_impact:
            print(f"\n📊 CATEGORY IMPACT:")
            for category, impact in sorted(category_impact.items(), key=lambda x: x[1]['impact_percentage'], reverse=True):
                impact_pct = impact['impact_percentage']
                status = "🔴" if impact_pct > 20 else "🟡" if impact_pct > 10 else "🟢"
                print(f"   {status} {category.replace('_', ' ').title()}: {impact_pct:.1f}% impact")
        
        # Handling capabilities
        impact_assessment = self.analysis_results.get('impact_assessment', {})
        if impact_assessment:
            print(f"\n🧪 CURRENT HANDLING CAPABILITIES:")
            for category, evaluation in impact_assessment.items():
                handling_rate = evaluation.get('handling_rate', 0)
                status = "🟢" if handling_rate > 75 else "🟡" if handling_rate > 50 else "🔴"
                print(f"   {status} {category.replace('_', ' ').title()}: {handling_rate:.1f}% handling rate")
        
        # Recommendations summary
        recommendations = self.analysis_results.get('robustness_recommendations', [])
        high_priority = [r for r in recommendations if r.get('priority') == 'high']
        medium_priority = [r for r in recommendations if r.get('priority') == 'medium']
        
        print(f"\n💡 RECOMMENDATIONS SUMMARY:")
        print(f"   🔴 High Priority: {len(high_priority)} recommendations")
        print(f"   🟡 Medium Priority: {len(medium_priority)} recommendations")
        
        # Overall assessment
        if edge_case_prevalence > 30:
            print(f"\n🔴 HIGH COMPLEXITY: {edge_case_prevalence:.1f}% edge case prevalence requires comprehensive framework")
        elif edge_case_prevalence > 15:
            print(f"\n🟡 MODERATE COMPLEXITY: {edge_case_prevalence:.1f}% edge case prevalence needs targeted improvements")
        else:
            print(f"\n🟢 LOW COMPLEXITY: {edge_case_prevalence:.1f}% edge case prevalence is manageable")
    
    def _setup_browser(self) -> webdriver.Chrome:
        """Setup browser for analysis"""
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Anti-detection measures
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver


def main():
    """Main function for edge case discovery and analysis"""
    
    print("🔍 Edge Case Discovery & Analysis Tool")
    print("Identifying and analyzing edge cases, boundary conditions, and unusual data formats...")
    print()
    
    try:
        # Initialize analyzer
        analyzer = EdgeCaseDiscoveryAnalyzer()
        
        # Run comprehensive analysis
        results = analyzer.discover_and_analyze_edge_cases()
        
        if 'error' not in results:
            print("\n✅ EDGE CASE DISCOVERY & ANALYSIS COMPLETED SUCCESSFULLY!")
            
            properties_analyzed = results.get('properties_analyzed', 0)
            frequency_data = results.get('frequency_analysis', {})
            edge_case_prevalence = frequency_data.get('edge_case_prevalence', 0)
            
            print(f"🏠 Properties analyzed: {properties_analyzed}")
            print(f"🔍 Edge case prevalence: {edge_case_prevalence:.1f}%")
            
            # Complexity assessment
            if edge_case_prevalence > 30:
                print(f"🔴 High complexity - comprehensive framework needed")
            elif edge_case_prevalence > 15:
                print(f"🟡 Moderate complexity - targeted improvements required")
            else:
                print(f"🟢 Low complexity - current approach sufficient")
            
        else:
            print(f"\n❌ EDGE CASE DISCOVERY & ANALYSIS FAILED: {results['error']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()
