#!/usr/bin/env python3
"""
Integration tests for all 6 refactored systems from Priority 2
Tests backward compatibility and module integration
"""

import unittest
import sqlite3
import tempfile
import os
from pathlib import Path


class TestRefactoredSystemsIntegration(unittest.TestCase):
    """Test integration of all refactored Priority 2 systems"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.temp_dir, "test.db")

    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_url_tracking_system_integration(self):
        """Test url_tracking_system.py refactored integration"""
        from url_tracking_system import URLTrackingSystem
        
        tracker = URLTrackingSystem(self.test_db)
        
        # Test basic operations
        url1 = "https://example.com/property1"
        url2 = "https://example.com/property2"
        
        # Add URLs
        self.assertTrue(tracker.add_url(url1, "gurgaon"))
        self.assertFalse(tracker.add_url(url1, "gurgaon"))  # Duplicate
        self.assertTrue(tracker.add_url(url2, "gurgaon"))
        
        # Check tracking
        self.assertTrue(tracker.is_url_tracked(url1))
        self.assertTrue(tracker.is_url_tracked(url2))
        
        # Get statistics
        stats = tracker.get_statistics()
        self.assertEqual(stats['total_urls'], 2)
        self.assertEqual(stats['unique_cities'], 1)

    def test_error_handling_system_integration(self):
        """Test error_handling_system.py refactored integration"""
        from error_handling_system import ErrorHandlingSystem
        
        error_handler = ErrorHandlingSystem(
            log_file=os.path.join(self.temp_dir, "errors.log"),
            enable_email=False
        )
        
        # Test error logging
        error_handler.log_error(
            error_type="SCRAPING_ERROR",
            message="Test error",
            severity="medium",
            context={"page": 1}
        )
        
        # Get statistics
        stats = error_handler.get_error_statistics()
        self.assertEqual(stats['total_errors'], 1)
        self.assertIn('medium', stats['by_severity'])

    def test_individual_property_tracking_integration(self):
        """Test individual_property_tracking_system.py refactored integration"""
        from individual_property_tracking_system import IndividualPropertyTrackingSystem
        
        tracker = IndividualPropertyTrackingSystem(self.test_db)
        
        # Test property tracking
        property_data = {
            'property_url': 'https://example.com/prop1',
            'title': 'Test Property',
            'price': '50 Lac',
            'location': 'Gurgaon'
        }
        
        # Add property
        result = tracker.add_property(property_data, session_id="test_session")
        self.assertTrue(result)
        
        # Check duplicate
        result = tracker.add_property(property_data, session_id="test_session")
        self.assertFalse(result)  # Should be duplicate
        
        # Get statistics
        stats = tracker.get_statistics()
        self.assertEqual(stats['total_properties'], 1)

    def test_advanced_security_system_integration(self):
        """Test advanced_security_system.py refactored integration"""
        from advanced_security_system import AdvancedSecuritySystem
        
        security = AdvancedSecuritySystem()
        
        # Test user agent rotation
        ua1 = security.get_random_user_agent()
        ua2 = security.get_random_user_agent()
        self.assertIsNotNone(ua1)
        self.assertIsNotNone(ua2)
        
        # Test delay calculation
        delay = security.calculate_smart_delay(base_delay=2.0)
        self.assertGreaterEqual(delay, 2.0)
        
        # Test headers generation
        headers = security.get_enhanced_headers()
        self.assertIn('User-Agent', headers)
        self.assertIn('Accept', headers)

    def test_performance_optimization_system_integration(self):
        """Test performance_optimization_system.py refactored integration"""
        from performance_optimization_system import PerformanceOptimizationSystem
        
        perf = PerformanceOptimizationSystem(
            cache_size=100,
            enable_profiling=True
        )
        
        # Test caching
        perf.cache_set("test_key", {"data": "test_value"})
        cached = perf.cache_get("test_key")
        self.assertEqual(cached['data'], "test_value")
        
        # Test profiling
        with perf.profile_operation("test_operation"):
            pass  # Simulate operation
        
        stats = perf.get_performance_stats()
        self.assertIn('cache_stats', stats)

    def test_advanced_dashboard_integration(self):
        """Test advanced_dashboard.py refactored integration"""
        # Dashboard requires GUI, so we test module imports only
        try:
            import dashboard_overview_tab
            import dashboard_sessions_tab
            import dashboard_performance_tab
            import dashboard_analytics_tab
            import dashboard_errors_tab
            import dashboard_refresh
            import dashboard_data_overview
            
            # Verify all modules have expected functions
            self.assertTrue(hasattr(dashboard_overview_tab, 'build_overview_tab'))
            self.assertTrue(hasattr(dashboard_sessions_tab, 'build_sessions_tab'))
            self.assertTrue(hasattr(dashboard_performance_tab, 'build_performance_tab'))
            self.assertTrue(hasattr(dashboard_analytics_tab, 'build_analytics_tab'))
            self.assertTrue(hasattr(dashboard_errors_tab, 'build_errors_tab'))
            self.assertTrue(hasattr(dashboard_refresh, 'setup_auto_refresh'))
            self.assertTrue(hasattr(dashboard_data_overview, 'load_overview_data'))
            
        except ImportError as e:
            self.fail(f"Dashboard module import failed: {e}")

    def test_all_systems_no_circular_dependencies(self):
        """Test that all refactored systems can be imported without circular dependencies"""
        try:
            from url_tracking_system import URLTrackingSystem
            from error_handling_system import ErrorHandlingSystem
            from individual_property_tracking_system import IndividualPropertyTrackingSystem
            from advanced_security_system import AdvancedSecuritySystem
            from performance_optimization_system import PerformanceOptimizationSystem
            from advanced_dashboard import AdvancedDashboard
            
            # If we get here, no circular dependencies
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Circular dependency detected: {e}")

    def test_backward_compatibility_url_tracking(self):
        """Test URLTrackingSystem maintains backward compatibility"""
        from url_tracking_system import URLTrackingSystem
        
        tracker = URLTrackingSystem(self.test_db)
        
        # Test all public methods exist
        self.assertTrue(hasattr(tracker, 'add_url'))
        self.assertTrue(hasattr(tracker, 'is_url_tracked'))
        self.assertTrue(hasattr(tracker, 'get_statistics'))
        self.assertTrue(hasattr(tracker, 'get_urls_by_city'))
        self.assertTrue(hasattr(tracker, 'cleanup_old_urls'))

    def test_backward_compatibility_error_handling(self):
        """Test ErrorHandlingSystem maintains backward compatibility"""
        from error_handling_system import ErrorHandlingSystem
        
        handler = ErrorHandlingSystem(
            log_file=os.path.join(self.temp_dir, "test.log"),
            enable_email=False
        )
        
        # Test all public methods exist
        self.assertTrue(hasattr(handler, 'log_error'))
        self.assertTrue(hasattr(handler, 'get_error_statistics'))
        self.assertTrue(hasattr(handler, 'get_recent_errors'))
        self.assertTrue(hasattr(handler, 'export_errors_to_csv'))

    def test_backward_compatibility_individual_tracking(self):
        """Test IndividualPropertyTrackingSystem maintains backward compatibility"""
        from individual_property_tracking_system import IndividualPropertyTrackingSystem
        
        tracker = IndividualPropertyTrackingSystem(self.test_db)
        
        # Test all public methods exist
        self.assertTrue(hasattr(tracker, 'add_property'))
        self.assertTrue(hasattr(tracker, 'is_duplicate'))
        self.assertTrue(hasattr(tracker, 'get_statistics'))
        self.assertTrue(hasattr(tracker, 'calculate_quality_score'))

    def test_backward_compatibility_security(self):
        """Test AdvancedSecuritySystem maintains backward compatibility"""
        from advanced_security_system import AdvancedSecuritySystem
        
        security = AdvancedSecuritySystem()
        
        # Test all public methods exist
        self.assertTrue(hasattr(security, 'get_random_user_agent'))
        self.assertTrue(hasattr(security, 'get_enhanced_headers'))
        self.assertTrue(hasattr(security, 'calculate_smart_delay'))
        self.assertTrue(hasattr(security, 'rotate_proxy'))

    def test_backward_compatibility_performance(self):
        """Test PerformanceOptimizationSystem maintains backward compatibility"""
        from performance_optimization_system import PerformanceOptimizationSystem
        
        perf = PerformanceOptimizationSystem()
        
        # Test all public methods exist
        self.assertTrue(hasattr(perf, 'cache_get'))
        self.assertTrue(hasattr(perf, 'cache_set'))
        self.assertTrue(hasattr(perf, 'profile_operation'))
        self.assertTrue(hasattr(perf, 'get_performance_stats'))
        self.assertTrue(hasattr(perf, 'optimize_memory'))


if __name__ == '__main__':
    unittest.main()

