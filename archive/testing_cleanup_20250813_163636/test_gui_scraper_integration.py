#!/usr/bin/env python3
"""
Test GUI-Scraper Integration
Verify that GUI controls are properly connected to scraper functionality
"""

import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gui_scraper_integration():
    """Test if GUI controls properly integrate with scraper"""
    
    print("🔗 GUI-SCRAPER INTEGRATION TESTING")
    print("=" * 60)
    
    try:
        from magicbricks_gui import MagicBricksGUI
        
        # Create GUI instance
        gui = MagicBricksGUI()
        print("✅ GUI instance created")
        
        # Test results
        results = {'passed': [], 'failed': [], 'warnings': []}
        
        def test_integration(name, test_func):
            try:
                result = test_func()
                if result['status'] == 'pass':
                    results['passed'].append(f"✅ {name}: {result['message']}")
                elif result['status'] == 'warning':
                    results['warnings'].append(f"⚠️ {name}: {result['message']}")
                else:
                    results['failed'].append(f"❌ {name}: {result['message']}")
            except Exception as e:
                results['failed'].append(f"❌ {name}: Exception - {str(e)}")
        
        # === TEST CONFIG INTEGRATION ===
        def test_config_values():
            """Test if GUI controls match config values"""
            if not hasattr(gui, 'config'):
                return {'status': 'fail', 'message': 'No config object found'}
            
            config = gui.config
            mismatches = []
            
            # Check key config mappings
            if hasattr(gui, 'max_pages_var'):
                gui_pages = int(gui.max_pages_var.get())
                config_pages = config.get('max_pages', 0)
                if gui_pages != config_pages:
                    mismatches.append(f"max_pages: GUI={gui_pages}, Config={config_pages}")
            
            if hasattr(gui, 'headless_var'):
                gui_headless = gui.headless_var.get()
                config_headless = config.get('headless', True)
                if gui_headless != config_headless:
                    mismatches.append(f"headless: GUI={gui_headless}, Config={config_headless}")
            
            if hasattr(gui, 'delay_var'):
                gui_delay = int(gui.delay_var.get())
                config_delay = config.get('page_delay', 3)
                if gui_delay != config_delay:
                    mismatches.append(f"page_delay: GUI={gui_delay}, Config={config_delay}")
            
            if mismatches:
                return {'status': 'warning', 'message': f'Config mismatches: {", ".join(mismatches)}'}
            else:
                return {'status': 'pass', 'message': 'GUI controls match config values'}
        
        test_integration("Config Value Sync", test_config_values)
        
        # === TEST SCRAPER METHODS ===
        def test_scraper_methods():
            """Test if scraper methods exist"""
            required_methods = ['start_scraping', 'stop_scraping', 'save_config']
            missing_methods = []
            
            for method in required_methods:
                if not hasattr(gui, method) or not callable(getattr(gui, method)):
                    missing_methods.append(method)
            
            if missing_methods:
                return {'status': 'fail', 'message': f'Missing methods: {", ".join(missing_methods)}'}
            else:
                return {'status': 'pass', 'message': 'All required scraper methods exist'}
        
        test_integration("Scraper Methods", test_scraper_methods)
        
        # === TEST CITY SYSTEM INTEGRATION ===
        def test_city_system():
            """Test city system integration"""
            if hasattr(gui, 'city_system'):
                cities = gui.city_system.cities if hasattr(gui.city_system, 'cities') else {}
                return {'status': 'pass', 'message': f'City system with {len(cities)} cities'}
            return {'status': 'fail', 'message': 'City system not found'}
        
        test_integration("City System", test_city_system)
        
        # === TEST ERROR HANDLING SYSTEM ===
        def test_error_system():
            """Test error handling system"""
            if hasattr(gui, 'error_system'):
                return {'status': 'pass', 'message': 'Error handling system exists'}
            return {'status': 'fail', 'message': 'Error handling system not found'}
        
        test_integration("Error Handling", test_error_system)
        
        # === TEST INDIVIDUAL PROPERTY FUNCTIONALITY ===
        def test_individual_property_controls():
            """Test individual property related controls"""
            issues = []
            
            # Check if individual pages toggle exists
            if not hasattr(gui, 'individual_pages_var'):
                issues.append('individual_pages_var missing')
            
            # Check if individual delay controls exist
            if not hasattr(gui, 'individual_delay_min_var'):
                issues.append('individual_delay_min_var missing')
            
            if not hasattr(gui, 'individual_delay_max_var'):
                issues.append('individual_delay_max_var missing')
            
            # Check if toggle method exists
            if not hasattr(gui, 'toggle_individual_delay_settings'):
                issues.append('toggle_individual_delay_settings method missing')
            
            if issues:
                return {'status': 'warning', 'message': f'Individual property issues: {", ".join(issues)}'}
            else:
                return {'status': 'pass', 'message': 'Individual property controls complete'}
        
        test_integration("Individual Property Controls", test_individual_property_controls)
        
        # === TEST FILTERING FUNCTIONALITY ===
        def test_filtering_controls():
            """Test property filtering controls"""
            issues = []
            
            # Check filtering variables
            filtering_vars = ['enable_filtering_var', 'price_min_var', 'price_max_var', 
                            'area_min_var', 'area_max_var']
            
            for var in filtering_vars:
                if not hasattr(gui, var):
                    issues.append(f'{var} missing')
            
            # Check BHK variables
            if not hasattr(gui, 'bhk_vars'):
                issues.append('bhk_vars missing')
            
            # Check toggle method
            if not hasattr(gui, 'toggle_filtering_options'):
                issues.append('toggle_filtering_options method missing')
            
            if issues:
                return {'status': 'warning', 'message': f'Filtering issues: {", ".join(issues)}'}
            else:
                return {'status': 'pass', 'message': 'Filtering controls complete'}
        
        test_integration("Filtering Controls", test_filtering_controls)
        
        # === TEST EXPORT FUNCTIONALITY ===
        def test_export_integration():
            """Test export functionality integration"""
            export_vars = ['export_json_var', 'export_excel_var']
            missing = []
            
            for var in export_vars:
                if not hasattr(gui, var):
                    missing.append(var)
            
            if missing:
                return {'status': 'warning', 'message': f'Missing export vars: {", ".join(missing)}'}
            else:
                return {'status': 'pass', 'message': 'Export controls complete'}
        
        test_integration("Export Integration", test_export_integration)
        
        # === TEST PERFORMANCE CONTROLS ===
        def test_performance_controls():
            """Test performance related controls"""
            perf_vars = ['batch_size_var', 'max_workers_var', 'memory_optimization_var']
            missing = []
            
            for var in perf_vars:
                if not hasattr(gui, var):
                    missing.append(var)
            
            if missing:
                return {'status': 'warning', 'message': f'Missing performance vars: {", ".join(missing)}'}
            else:
                return {'status': 'pass', 'message': 'Performance controls complete'}
        
        test_integration("Performance Controls", test_performance_controls)
        
        # === TEST BROWSER SETTINGS ===
        def test_browser_settings():
            """Test browser configuration controls"""
            browser_vars = ['page_load_strategy_var', 'disable_images_var', 'disable_css_var', 'disable_js_var']
            missing = []
            
            for var in browser_vars:
                if not hasattr(gui, var):
                    missing.append(var)
            
            if missing:
                return {'status': 'warning', 'message': f'Missing browser vars: {", ".join(missing)}'}
            else:
                return {'status': 'pass', 'message': 'Browser settings complete'}
        
        test_integration("Browser Settings", test_browser_settings)
        
        # Close GUI
        gui.root.after(100, gui.root.destroy)
        gui.root.mainloop()
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST RESULTS")
        print("=" * 60)
        
        print(f"\n✅ PASSED ({len(results['passed'])}):")
        for r in results['passed']:
            print(f"  {r}")
        
        print(f"\n⚠️ WARNINGS ({len(results['warnings'])}):")
        for r in results['warnings']:
            print(f"  {r}")
        
        print(f"\n❌ FAILED ({len(results['failed'])}):")
        for r in results['failed']:
            print(f"  {r}")
        
        total = len(results['passed']) + len(results['warnings']) + len(results['failed'])
        success = (len(results['passed']) / total * 100) if total > 0 else 0
        
        print(f"\n📈 INTEGRATION SUCCESS RATE: {success:.1f}% ({len(results['passed'])}/{total})")
        
        return results
        
    except Exception as e:
        print(f"❌ Critical integration error: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_gui_scraper_integration()
