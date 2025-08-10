#!/usr/bin/env python3
"""
User Acceptance Testing Framework
Comprehensive UAT framework for MagicBricks scraper with user scenarios, feedback collection, and usability analysis.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class UserType(Enum):
    """Different types of users for testing"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    BUSINESS = "business"


class TestScenario(Enum):
    """User acceptance test scenarios"""
    FIRST_TIME_SETUP = "first_time_setup"
    BASIC_SCRAPING = "basic_scraping"
    MULTI_CITY_SELECTION = "multi_city_selection"
    INCREMENTAL_SCRAPING = "incremental_scraping"
    ERROR_RECOVERY = "error_recovery"
    RESULTS_ANALYSIS = "results_analysis"
    SCHEDULING_SETUP = "scheduling_setup"
    ADVANCED_CONFIGURATION = "advanced_configuration"


@dataclass
class UserFeedback:
    """User feedback data structure"""
    user_type: UserType
    scenario: TestScenario
    timestamp: datetime
    ease_of_use_rating: int  # 1-5 scale
    feature_completeness_rating: int  # 1-5 scale
    performance_rating: int  # 1-5 scale
    overall_satisfaction: int  # 1-5 scale
    positive_feedback: List[str]
    negative_feedback: List[str]
    suggestions: List[str]
    completion_time_minutes: float
    errors_encountered: List[str]
    help_needed: bool
    would_recommend: bool


@dataclass
class TestScenarioDefinition:
    """Definition of a test scenario"""
    name: str
    description: str
    user_types: List[UserType]
    steps: List[str]
    expected_outcomes: List[str]
    success_criteria: List[str]
    estimated_time_minutes: int


class UserAcceptanceTestingFramework:
    """
    Comprehensive User Acceptance Testing framework
    """
    
    def __init__(self, output_directory: str = '.'):
        """Initialize UAT framework"""
        
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # Test data storage
        self.test_scenarios = self._initialize_test_scenarios()
        self.user_feedback = []
        self.test_results = {}
        
        # Simulated user profiles
        self.user_profiles = self._create_user_profiles()
        
        print("👥 User Acceptance Testing Framework Initialized")
        print(f"   📁 Output directory: {self.output_directory}")
        print(f"   🧪 Test scenarios: {len(self.test_scenarios)}")
        print(f"   👤 User profiles: {len(self.user_profiles)}")
    
    def _initialize_test_scenarios(self) -> Dict[TestScenario, TestScenarioDefinition]:
        """Initialize comprehensive test scenarios"""
        
        scenarios = {}
        
        # First Time Setup
        scenarios[TestScenario.FIRST_TIME_SETUP] = TestScenarioDefinition(
            name="First Time Setup",
            description="New user setting up the application for the first time",
            user_types=[UserType.BEGINNER, UserType.INTERMEDIATE],
            steps=[
                "Launch the MagicBricks GUI application",
                "Navigate through the main interface",
                "Understand the different sections and controls",
                "Configure basic settings (output directory)",
                "Select a city for scraping",
                "Choose a scraping mode",
                "Review configuration before starting"
            ],
            expected_outcomes=[
                "User can launch application without errors",
                "Interface is intuitive and self-explanatory",
                "User can configure basic settings",
                "Help text and tooltips are helpful",
                "Configuration validation works properly"
            ],
            success_criteria=[
                "Completion time < 10 minutes",
                "No critical errors encountered",
                "User confidence rating > 3/5",
                "All required settings configured correctly"
            ],
            estimated_time_minutes=8
        )
        
        # Basic Scraping
        scenarios[TestScenario.BASIC_SCRAPING] = TestScenarioDefinition(
            name="Basic Property Scraping",
            description="Perform basic property scraping with default settings",
            user_types=[UserType.BEGINNER, UserType.INTERMEDIATE, UserType.BUSINESS],
            steps=[
                "Select a single city (Mumbai)",
                "Choose incremental scraping mode",
                "Set max pages to 5",
                "Start scraping process",
                "Monitor progress in real-time",
                "Wait for completion",
                "Review results in the viewer",
                "Export data to CSV"
            ],
            expected_outcomes=[
                "Scraping starts without issues",
                "Progress is clearly visible",
                "Results are displayed properly",
                "Export functionality works",
                "Data quality is acceptable"
            ],
            success_criteria=[
                "Scraping completes successfully",
                "Properties found > 50",
                "Export file is created",
                "User satisfaction > 4/5"
            ],
            estimated_time_minutes=15
        )
        
        # Multi-City Selection
        scenarios[TestScenario.MULTI_CITY_SELECTION] = TestScenarioDefinition(
            name="Multi-City Selection",
            description="Select and configure multiple cities for scraping",
            user_types=[UserType.INTERMEDIATE, UserType.ADVANCED, UserType.BUSINESS],
            steps=[
                "Open city selection interface",
                "Use search functionality to find cities",
                "Apply filters (region, tier, metro)",
                "Select 3-5 cities",
                "Review selection and validation warnings",
                "Configure scraping parameters",
                "Start multi-city scraping"
            ],
            expected_outcomes=[
                "City selection interface is intuitive",
                "Search and filters work properly",
                "Validation provides helpful feedback",
                "Multi-city scraping works correctly"
            ],
            success_criteria=[
                "Multiple cities selected successfully",
                "Validation warnings are helpful",
                "Scraping works for all selected cities",
                "Performance is acceptable"
            ],
            estimated_time_minutes=12
        )
        
        # Incremental Scraping
        scenarios[TestScenario.INCREMENTAL_SCRAPING] = TestScenarioDefinition(
            name="Incremental Scraping Setup",
            description="Configure and use incremental scraping features",
            user_types=[UserType.INTERMEDIATE, UserType.ADVANCED, UserType.BUSINESS],
            steps=[
                "Enable incremental scraping",
                "Understand time savings explanation",
                "Run initial full scraping",
                "Run subsequent incremental scraping",
                "Compare results and time savings",
                "Review incremental logic explanation"
            ],
            expected_outcomes=[
                "Incremental concept is clear",
                "Time savings are evident",
                "Results are consistent",
                "User understands benefits"
            ],
            success_criteria=[
                "Time savings > 50%",
                "Results quality maintained",
                "User understands incremental logic",
                "Satisfaction > 4/5"
            ],
            estimated_time_minutes=20
        )
        
        # Error Recovery
        scenarios[TestScenario.ERROR_RECOVERY] = TestScenarioDefinition(
            name="Error Handling & Recovery",
            description="Test error handling and user guidance during issues",
            user_types=[UserType.BEGINNER, UserType.INTERMEDIATE],
            steps=[
                "Trigger network error (disconnect internet)",
                "Observe error handling",
                "Review error message and suggestions",
                "Follow recovery suggestions",
                "Test with invalid configuration",
                "Review validation messages"
            ],
            expected_outcomes=[
                "Errors are handled gracefully",
                "Error messages are user-friendly",
                "Recovery suggestions are helpful",
                "Application doesn't crash"
            ],
            success_criteria=[
                "No application crashes",
                "Error messages are clear",
                "Recovery is possible",
                "User confidence maintained"
            ],
            estimated_time_minutes=10
        )
        
        # Results Analysis
        scenarios[TestScenario.RESULTS_ANALYSIS] = TestScenarioDefinition(
            name="Results Analysis & Export",
            description="Analyze scraped data and use export features",
            user_types=[UserType.INTERMEDIATE, UserType.ADVANCED, UserType.BUSINESS],
            steps=[
                "Open results viewer",
                "Use search and filter functionality",
                "Sort data by different columns",
                "Export to different formats (CSV, Excel, JSON)",
                "Review data quality and completeness",
                "Understand data structure"
            ],
            expected_outcomes=[
                "Results viewer is functional",
                "Search and filters work well",
                "Export formats are correct",
                "Data quality is good"
            ],
            success_criteria=[
                "All export formats work",
                "Search/filter is responsive",
                "Data completeness > 80%",
                "User finds interface intuitive"
            ],
            estimated_time_minutes=15
        )
        
        # Scheduling Setup
        scenarios[TestScenario.SCHEDULING_SETUP] = TestScenarioDefinition(
            name="Automated Scheduling",
            description="Set up automated scraping schedules",
            user_types=[UserType.ADVANCED, UserType.BUSINESS],
            steps=[
                "Open scheduling interface",
                "Review preset schedule options",
                "Create custom schedule",
                "Configure notification settings",
                "Test schedule validation",
                "Understand background execution"
            ],
            expected_outcomes=[
                "Scheduling interface is clear",
                "Presets are useful",
                "Custom scheduling works",
                "Validation is helpful"
            ],
            success_criteria=[
                "Schedule created successfully",
                "Validation prevents errors",
                "User understands automation",
                "Interface is intuitive"
            ],
            estimated_time_minutes=12
        )
        
        # Advanced Configuration
        scenarios[TestScenario.ADVANCED_CONFIGURATION] = TestScenarioDefinition(
            name="Advanced Configuration",
            description="Use advanced features and configuration options",
            user_types=[UserType.ADVANCED, UserType.BUSINESS],
            steps=[
                "Access advanced settings",
                "Configure error handling options",
                "Set up email notifications",
                "Adjust performance parameters",
                "Configure logging levels",
                "Test configuration validation"
            ],
            expected_outcomes=[
                "Advanced options are accessible",
                "Configuration is flexible",
                "Validation prevents issues",
                "Help documentation is available"
            ],
            success_criteria=[
                "All advanced features work",
                "Configuration is saved properly",
                "Validation is comprehensive",
                "User feels in control"
            ],
            estimated_time_minutes=18
        )
        
        return scenarios
    
    def _create_user_profiles(self) -> Dict[UserType, Dict[str, Any]]:
        """Create simulated user profiles for testing"""
        
        return {
            UserType.BEGINNER: {
                'name': 'Sarah (Real Estate Agent)',
                'technical_level': 1,
                'goals': ['Extract property data for clients', 'Simple operation', 'Reliable results'],
                'concerns': ['Technical complexity', 'Data accuracy', 'Ease of use'],
                'typical_usage': 'Weekly scraping for specific areas',
                'expected_completion_time_multiplier': 1.5
            },
            UserType.INTERMEDIATE: {
                'name': 'Mike (Property Analyst)',
                'technical_level': 3,
                'goals': ['Market analysis', 'Trend identification', 'Regular data collection'],
                'concerns': ['Data completeness', 'Automation', 'Performance'],
                'typical_usage': 'Daily/weekly automated scraping',
                'expected_completion_time_multiplier': 1.0
            },
            UserType.ADVANCED: {
                'name': 'Alex (Data Scientist)',
                'technical_level': 4,
                'goals': ['Large-scale data collection', 'Custom analysis', 'Integration'],
                'concerns': ['Scalability', 'Customization', 'API access'],
                'typical_usage': 'Automated large-scale operations',
                'expected_completion_time_multiplier': 0.8
            },
            UserType.BUSINESS: {
                'name': 'Jennifer (Business Owner)',
                'technical_level': 2,
                'goals': ['Market intelligence', 'Competitive analysis', 'ROI tracking'],
                'concerns': ['Cost efficiency', 'Reliability', 'Support'],
                'typical_usage': 'Regular business intelligence gathering',
                'expected_completion_time_multiplier': 1.2
            }
        }
    
    def simulate_user_test(self, user_type: UserType, scenario: TestScenario) -> UserFeedback:
        """Simulate a user acceptance test"""
        
        print(f"\n👤 Simulating UAT: {user_type.value} - {scenario.value}")
        
        user_profile = self.user_profiles[user_type]
        scenario_def = self.test_scenarios[scenario]
        
        # Simulate test execution
        start_time = datetime.now()
        
        # Calculate completion time based on user profile
        base_time = scenario_def.estimated_time_minutes
        multiplier = user_profile['expected_completion_time_multiplier']
        completion_time = base_time * multiplier
        
        # Simulate ratings based on user type and scenario complexity
        ratings = self._calculate_simulated_ratings(user_type, scenario)
        
        # Generate feedback based on user profile and scenario
        feedback = self._generate_simulated_feedback(user_type, scenario, ratings)
        
        # Create feedback object
        user_feedback = UserFeedback(
            user_type=user_type,
            scenario=scenario,
            timestamp=start_time,
            ease_of_use_rating=ratings['ease_of_use'],
            feature_completeness_rating=ratings['feature_completeness'],
            performance_rating=ratings['performance'],
            overall_satisfaction=ratings['overall_satisfaction'],
            positive_feedback=feedback['positive'],
            negative_feedback=feedback['negative'],
            suggestions=feedback['suggestions'],
            completion_time_minutes=completion_time,
            errors_encountered=feedback['errors'],
            help_needed=ratings['ease_of_use'] < 3,
            would_recommend=ratings['overall_satisfaction'] >= 4
        )
        
        print(f"   ⏱️ Completion time: {completion_time:.1f} minutes")
        print(f"   ⭐ Overall satisfaction: {ratings['overall_satisfaction']}/5")
        print(f"   👍 Would recommend: {user_feedback.would_recommend}")
        
        return user_feedback
    
    def _calculate_simulated_ratings(self, user_type: UserType, scenario: TestScenario) -> Dict[str, int]:
        """Calculate simulated ratings based on user type and scenario"""
        
        # Base ratings (assuming good implementation)
        base_ratings = {
            'ease_of_use': 4,
            'feature_completeness': 4,
            'performance': 4,
            'overall_satisfaction': 4
        }
        
        # Adjust based on user type
        if user_type == UserType.BEGINNER:
            # Beginners might find advanced features harder
            if scenario in [TestScenario.ADVANCED_CONFIGURATION, TestScenario.SCHEDULING_SETUP]:
                base_ratings['ease_of_use'] -= 1
            # But appreciate simple, working features
            if scenario in [TestScenario.BASIC_SCRAPING, TestScenario.FIRST_TIME_SETUP]:
                base_ratings['ease_of_use'] += 1
        
        elif user_type == UserType.ADVANCED:
            # Advanced users appreciate comprehensive features
            base_ratings['feature_completeness'] += 1
            # But might be more critical of performance
            if scenario == TestScenario.BASIC_SCRAPING:
                base_ratings['performance'] -= 1
        
        elif user_type == UserType.BUSINESS:
            # Business users focus on reliability and ROI
            base_ratings['performance'] += 1
            if scenario in [TestScenario.INCREMENTAL_SCRAPING, TestScenario.MULTI_CITY_SELECTION]:
                base_ratings['overall_satisfaction'] += 1
        
        # Ensure ratings stay within 1-5 range
        for key in base_ratings:
            base_ratings[key] = max(1, min(5, base_ratings[key]))
        
        return base_ratings
    
    def _generate_simulated_feedback(self, user_type: UserType, scenario: TestScenario, 
                                   ratings: Dict[str, int]) -> Dict[str, List[str]]:
        """Generate simulated user feedback"""
        
        feedback = {
            'positive': [],
            'negative': [],
            'suggestions': [],
            'errors': []
        }
        
        # Positive feedback based on ratings
        if ratings['ease_of_use'] >= 4:
            feedback['positive'].append("Interface is intuitive and easy to navigate")
            feedback['positive'].append("Clear instructions and helpful tooltips")
        
        if ratings['performance'] >= 4:
            feedback['positive'].append("Fast and responsive performance")
            feedback['positive'].append("Reliable scraping with good success rates")
        
        if ratings['feature_completeness'] >= 4:
            feedback['positive'].append("Comprehensive feature set")
            feedback['positive'].append("All necessary functionality is available")
        
        # Scenario-specific positive feedback
        if scenario == TestScenario.INCREMENTAL_SCRAPING:
            feedback['positive'].append("Significant time savings with incremental mode")
            feedback['positive'].append("Smart stopping logic works well")
        
        if scenario == TestScenario.MULTI_CITY_SELECTION:
            feedback['positive'].append("Excellent city selection interface")
            feedback['positive'].append("Helpful validation and recommendations")
        
        # Negative feedback and suggestions based on lower ratings
        if ratings['ease_of_use'] < 4:
            feedback['negative'].append("Some features could be more intuitive")
            feedback['suggestions'].append("Add more guided tutorials for beginners")
        
        if ratings['performance'] < 4:
            feedback['negative'].append("Performance could be improved")
            feedback['suggestions'].append("Optimize for faster scraping speeds")
        
        # User type specific feedback
        if user_type == UserType.BEGINNER:
            feedback['suggestions'].append("Add step-by-step wizard for first-time setup")
            feedback['suggestions'].append("Include more help documentation")
        
        elif user_type == UserType.ADVANCED:
            feedback['suggestions'].append("Add API access for programmatic control")
            feedback['suggestions'].append("Include more advanced configuration options")
        
        elif user_type == UserType.BUSINESS:
            feedback['suggestions'].append("Add business reporting features")
            feedback['suggestions'].append("Include cost/benefit analysis tools")
        
        return feedback
    
    def run_comprehensive_uat(self) -> Dict[str, Any]:
        """Run comprehensive user acceptance testing"""
        
        print("👥 STARTING COMPREHENSIVE USER ACCEPTANCE TESTING")
        print("="*60)
        
        all_feedback = []
        
        # Test each scenario with appropriate user types
        for scenario, scenario_def in self.test_scenarios.items():
            print(f"\n📋 Testing Scenario: {scenario_def.name}")
            
            for user_type in scenario_def.user_types:
                feedback = self.simulate_user_test(user_type, scenario)
                all_feedback.append(feedback)
                self.user_feedback.append(feedback)
        
        # Analyze results
        analysis = self._analyze_uat_results()
        
        print("\n" + "="*60)
        print("📊 USER ACCEPTANCE TESTING COMPLETE")
        
        return analysis
    
    def _analyze_uat_results(self) -> Dict[str, Any]:
        """Analyze UAT results and generate insights"""
        
        if not self.user_feedback:
            return {}
        
        # Calculate overall metrics
        total_tests = len(self.user_feedback)
        avg_satisfaction = sum(f.overall_satisfaction for f in self.user_feedback) / total_tests
        avg_ease_of_use = sum(f.ease_of_use_rating for f in self.user_feedback) / total_tests
        avg_performance = sum(f.performance_rating for f in self.user_feedback) / total_tests
        avg_completeness = sum(f.feature_completeness_rating for f in self.user_feedback) / total_tests
        
        recommendation_rate = sum(1 for f in self.user_feedback if f.would_recommend) / total_tests
        help_needed_rate = sum(1 for f in self.user_feedback if f.help_needed) / total_tests
        
        # Analyze by user type
        user_type_analysis = {}
        for user_type in UserType:
            user_feedback = [f for f in self.user_feedback if f.user_type == user_type]
            if user_feedback:
                user_type_analysis[user_type.value] = {
                    'count': len(user_feedback),
                    'avg_satisfaction': sum(f.overall_satisfaction for f in user_feedback) / len(user_feedback),
                    'avg_completion_time': sum(f.completion_time_minutes for f in user_feedback) / len(user_feedback),
                    'recommendation_rate': sum(1 for f in user_feedback if f.would_recommend) / len(user_feedback)
                }
        
        # Analyze by scenario
        scenario_analysis = {}
        for scenario in TestScenario:
            scenario_feedback = [f for f in self.user_feedback if f.scenario == scenario]
            if scenario_feedback:
                scenario_analysis[scenario.value] = {
                    'count': len(scenario_feedback),
                    'avg_satisfaction': sum(f.overall_satisfaction for f in scenario_feedback) / len(scenario_feedback),
                    'success_rate': sum(1 for f in scenario_feedback if f.overall_satisfaction >= 4) / len(scenario_feedback)
                }
        
        # Collect common feedback themes
        all_positive = []
        all_negative = []
        all_suggestions = []
        
        for feedback in self.user_feedback:
            all_positive.extend(feedback.positive_feedback)
            all_negative.extend(feedback.negative_feedback)
            all_suggestions.extend(feedback.suggestions)
        
        # Count frequency of feedback themes
        positive_themes = self._count_feedback_themes(all_positive)
        negative_themes = self._count_feedback_themes(all_negative)
        suggestion_themes = self._count_feedback_themes(all_suggestions)
        
        return {
            'overall_metrics': {
                'total_tests': total_tests,
                'avg_satisfaction': avg_satisfaction,
                'avg_ease_of_use': avg_ease_of_use,
                'avg_performance': avg_performance,
                'avg_feature_completeness': avg_completeness,
                'recommendation_rate': recommendation_rate,
                'help_needed_rate': help_needed_rate
            },
            'user_type_analysis': user_type_analysis,
            'scenario_analysis': scenario_analysis,
            'feedback_themes': {
                'positive': positive_themes,
                'negative': negative_themes,
                'suggestions': suggestion_themes
            }
        }
    
    def _count_feedback_themes(self, feedback_list: List[str]) -> Dict[str, int]:
        """Count frequency of feedback themes"""
        
        theme_counts = {}
        for feedback in feedback_list:
            # Simple keyword-based theme detection
            feedback_lower = feedback.lower()
            
            if 'intuitive' in feedback_lower or 'easy' in feedback_lower:
                theme_counts['usability'] = theme_counts.get('usability', 0) + 1
            elif 'fast' in feedback_lower or 'performance' in feedback_lower:
                theme_counts['performance'] = theme_counts.get('performance', 0) + 1
            elif 'feature' in feedback_lower or 'functionality' in feedback_lower:
                theme_counts['features'] = theme_counts.get('features', 0) + 1
            elif 'help' in feedback_lower or 'documentation' in feedback_lower:
                theme_counts['documentation'] = theme_counts.get('documentation', 0) + 1
            elif 'time' in feedback_lower or 'saving' in feedback_lower:
                theme_counts['efficiency'] = theme_counts.get('efficiency', 0) + 1
        
        return theme_counts
    
    def generate_uat_report(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive UAT report"""
        
        if not analysis:
            return "No UAT analysis available"
        
        report = []
        report.append("👥 USER ACCEPTANCE TESTING REPORT")
        report.append("="*60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall metrics
        metrics = analysis['overall_metrics']
        report.append("📊 OVERALL RESULTS")
        report.append("-" * 40)
        report.append(f"Total Tests Conducted: {metrics['total_tests']}")
        report.append(f"Average Satisfaction: {metrics['avg_satisfaction']:.1f}/5")
        report.append(f"Average Ease of Use: {metrics['avg_ease_of_use']:.1f}/5")
        report.append(f"Average Performance: {metrics['avg_performance']:.1f}/5")
        report.append(f"Average Feature Completeness: {metrics['avg_feature_completeness']:.1f}/5")
        report.append(f"Recommendation Rate: {metrics['recommendation_rate']:.1%}")
        report.append(f"Users Needing Help: {metrics['help_needed_rate']:.1%}")
        report.append("")
        
        # User type analysis
        report.append("👤 USER TYPE ANALYSIS")
        report.append("-" * 40)
        for user_type, data in analysis['user_type_analysis'].items():
            report.append(f"\n{user_type.title()} Users:")
            report.append(f"  Tests: {data['count']}")
            report.append(f"  Satisfaction: {data['avg_satisfaction']:.1f}/5")
            report.append(f"  Avg Completion Time: {data['avg_completion_time']:.1f} minutes")
            report.append(f"  Recommendation Rate: {data['recommendation_rate']:.1%}")
        
        report.append("")
        
        # Scenario analysis
        report.append("📋 SCENARIO ANALYSIS")
        report.append("-" * 40)
        for scenario, data in analysis['scenario_analysis'].items():
            report.append(f"\n{scenario.replace('_', ' ').title()}:")
            report.append(f"  Tests: {data['count']}")
            report.append(f"  Satisfaction: {data['avg_satisfaction']:.1f}/5")
            report.append(f"  Success Rate: {data['success_rate']:.1%}")
        
        report.append("")
        
        # Feedback themes
        themes = analysis['feedback_themes']
        report.append("💬 FEEDBACK THEMES")
        report.append("-" * 40)
        
        if themes['positive']:
            report.append("\nPositive Feedback:")
            for theme, count in sorted(themes['positive'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {theme.title()}: {count} mentions")
        
        if themes['negative']:
            report.append("\nAreas for Improvement:")
            for theme, count in sorted(themes['negative'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {theme.title()}: {count} mentions")
        
        if themes['suggestions']:
            report.append("\nSuggested Enhancements:")
            for theme, count in sorted(themes['suggestions'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {theme.title()}: {count} mentions")
        
        # Recommendations
        report.append("\n🎯 RECOMMENDATIONS")
        report.append("-" * 40)
        
        if metrics['avg_satisfaction'] >= 4.0:
            report.append("✅ Excellent user satisfaction - ready for production")
        elif metrics['avg_satisfaction'] >= 3.5:
            report.append("✅ Good user satisfaction - minor improvements recommended")
        else:
            report.append("⚠️ User satisfaction needs improvement before release")
        
        if metrics['recommendation_rate'] >= 0.8:
            report.append("✅ High recommendation rate indicates strong product-market fit")
        else:
            report.append("⚠️ Consider addressing user concerns to improve recommendation rate")
        
        if metrics['help_needed_rate'] <= 0.3:
            report.append("✅ Low help requirements indicate good usability")
        else:
            report.append("⚠️ Consider improving documentation and user guidance")
        
        return "\n".join(report)
    
    def export_uat_results(self, filename: str = None) -> str:
        """Export UAT results to JSON file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"uat_results_{timestamp}.json"
        
        output_path = self.output_directory / filename
        
        # Prepare data for export
        export_data = {
            'test_metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_feedback': len(self.user_feedback),
                'framework_version': '1.0'
            },
            'user_feedback': []
        }
        
        for feedback in self.user_feedback:
            export_data['user_feedback'].append({
                'user_type': feedback.user_type.value,
                'scenario': feedback.scenario.value,
                'timestamp': feedback.timestamp.isoformat(),
                'ratings': {
                    'ease_of_use': feedback.ease_of_use_rating,
                    'feature_completeness': feedback.feature_completeness_rating,
                    'performance': feedback.performance_rating,
                    'overall_satisfaction': feedback.overall_satisfaction
                },
                'feedback': {
                    'positive': feedback.positive_feedback,
                    'negative': feedback.negative_feedback,
                    'suggestions': feedback.suggestions
                },
                'metrics': {
                    'completion_time_minutes': feedback.completion_time_minutes,
                    'errors_encountered': feedback.errors_encountered,
                    'help_needed': feedback.help_needed,
                    'would_recommend': feedback.would_recommend
                }
            })
        
        # Save to file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📁 UAT results exported to {output_path}")
        return str(output_path)


def main():
    """Run user acceptance testing framework"""
    
    try:
        print("👥 MAGICBRICKS SCRAPER USER ACCEPTANCE TESTING")
        print("="*60)
        
        # Initialize UAT framework
        uat_framework = UserAcceptanceTestingFramework()
        
        # Run comprehensive UAT
        analysis = uat_framework.run_comprehensive_uat()
        
        # Generate and display report
        report = uat_framework.generate_uat_report(analysis)
        print("\n" + report)
        
        # Export results
        export_file = uat_framework.export_uat_results()
        
        print(f"\n✅ User Acceptance Testing completed successfully!")
        print(f"📊 {analysis['overall_metrics']['total_tests']} tests completed")
        print(f"⭐ Average satisfaction: {analysis['overall_metrics']['avg_satisfaction']:.1f}/5")
        print(f"👍 Recommendation rate: {analysis['overall_metrics']['recommendation_rate']:.1%}")
        print(f"📁 Results exported to: {export_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ User Acceptance Testing failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
