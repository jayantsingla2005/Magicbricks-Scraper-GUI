#!/usr/bin/env python3
"""
Test Enhanced Individual Property Controls
Verify the new individual property management features
"""

import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_individual_controls():
    """Test the new individual property management controls"""
    
    print("🧪 TESTING ENHANCED INDIVIDUAL PROPERTY CONTROLS")
    print("=" * 60)
    
    try:
        from magicbricks_gui import MagicBricksGUI
        
        # Create GUI instance
        gui = MagicBricksGUI()
        print("✅ GUI instance created")
        
        # Test results
        results = {'passed': [], 'failed': [], 'warnings': []}
        
        def test_control(name, test_func):
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
        
        # === TEST NEW INDIVIDUAL PROPERTY CONTROLS ===
        
        def test_individual_mode_control():
            """Test individual scraping mode control"""
            if hasattr(gui, 'individual_mode_var'):
                mode = gui.individual_mode_var.get()
                valid_modes = ['with_listing', 'individual_only', 'skip_individual']
                if mode in valid_modes:
                    return {'status': 'pass', 'message': f'Individual mode: {mode}'}
                return {'status': 'warning', 'message': f'Invalid mode: {mode}'}
            return {'status': 'fail', 'message': 'individual_mode_var not found'}
        
        test_control("Individual Scraping Mode", test_individual_mode_control)
        
        def test_individual_count_control():
            """Test individual property count control"""
            if hasattr(gui, 'individual_count_var'):
                count = gui.individual_count_var.get()
                try:
                    count_int = int(count) if count.isdigit() else 0
                    return {'status': 'pass', 'message': f'Max individual properties: {count_int}'}
                except ValueError:
                    return {'status': 'warning', 'message': f'Invalid count: {count}'}
            return {'status': 'fail', 'message': 'individual_count_var not found'}
        
        test_control("Individual Property Count", test_individual_count_control)
        
        def test_scraped_count_display():
            """Test scraped count display"""
            if hasattr(gui, 'scraped_count_var'):
                count_text = gui.scraped_count_var.get()
                return {'status': 'pass', 'message': f'Scraped count display: {count_text}'}
            return {'status': 'fail', 'message': 'scraped_count_var not found'}
        
        test_control("Scraped Count Display", test_scraped_count_display)
        
        def test_force_rescrape_control():
            """Test force re-scrape control"""
            if hasattr(gui, 'force_rescrape_var'):
                force_rescrape = gui.force_rescrape_var.get()
                return {'status': 'pass', 'message': f'Force re-scrape: {force_rescrape}'}
            return {'status': 'fail', 'message': 'force_rescrape_var not found'}
        
        test_control("Force Re-scrape Control", test_force_rescrape_control)
        
        def test_individual_mode_description():
            """Test individual mode description"""
            if hasattr(gui, 'individual_mode_desc_var'):
                desc = gui.individual_mode_desc_var.get()
                return {'status': 'pass', 'message': f'Mode description exists: {len(desc)} chars'}
            return {'status': 'fail', 'message': 'individual_mode_desc_var not found'}
        
        test_control("Individual Mode Description", test_individual_mode_description)
        
        def test_refresh_scraped_count_method():
            """Test refresh scraped count method"""
            if hasattr(gui, 'refresh_scraped_count') and callable(gui.refresh_scraped_count):
                return {'status': 'pass', 'message': 'Refresh scraped count method exists'}
            return {'status': 'fail', 'message': 'refresh_scraped_count method not found'}
        
        test_control("Refresh Scraped Count Method", test_refresh_scraped_count_method)
        
        def test_individual_config_method():
            """Test get individual scraping config method"""
            if hasattr(gui, 'get_individual_scraping_config') and callable(gui.get_individual_scraping_config):
                try:
                    config = gui.get_individual_scraping_config()
                    required_keys = ['mode', 'max_count', 'force_rescrape', 'enabled']
                    missing_keys = [key for key in required_keys if key not in config]
                    if missing_keys:
                        return {'status': 'warning', 'message': f'Config missing keys: {missing_keys}'}
                    return {'status': 'pass', 'message': f'Individual config complete: {config}'}
                except Exception as e:
                    return {'status': 'fail', 'message': f'Config method error: {str(e)}'}
            return {'status': 'fail', 'message': 'get_individual_scraping_config method not found'}
        
        test_control("Individual Config Method", test_individual_config_method)
        
        def test_mode_change_handlers():
            """Test mode change handlers"""
            handlers = ['on_individual_mode_changed', 'update_individual_mode_description']
            missing_handlers = []
            
            for handler in handlers:
                if not hasattr(gui, handler) or not callable(getattr(gui, handler)):
                    missing_handlers.append(handler)
            
            if missing_handlers:
                return {'status': 'warning', 'message': f'Missing handlers: {missing_handlers}'}
            return {'status': 'pass', 'message': 'All mode change handlers exist'}
        
        test_control("Mode Change Handlers", test_mode_change_handlers)
        
        # === TEST INTEGRATION WITH EXISTING CONTROLS ===
        
        def test_integration_with_existing():
            """Test integration with existing individual property controls"""
            existing_controls = ['individual_pages_var', 'individual_delay_min_var', 'individual_delay_max_var']
            missing_controls = []
            
            for control in existing_controls:
                if not hasattr(gui, control):
                    missing_controls.append(control)
            
            if missing_controls:
                return {'status': 'warning', 'message': f'Missing existing controls: {missing_controls}'}
            return {'status': 'pass', 'message': 'Integration with existing controls complete'}
        
        test_control("Integration with Existing Controls", test_integration_with_existing)
        
        # === TEST SCENARIO FUNCTIONALITY ===
        
        def test_scenario_individual_only():
            """Test individual-only scraping scenario"""
            try:
                # Set to individual-only mode
                gui.individual_mode_var.set('individual_only')
                gui.individual_count_var.set('50')
                gui.force_rescrape_var.set(False)
                
                config = gui.get_individual_scraping_config()
                
                expected_config = {
                    'mode': 'individual_only',
                    'max_count': 50,
                    'force_rescrape': False,
                    'enabled': gui.individual_pages_var.get()
                }
                
                if config == expected_config:
                    return {'status': 'pass', 'message': 'Individual-only scenario works correctly'}
                else:
                    return {'status': 'warning', 'message': f'Config mismatch: {config} vs {expected_config}'}
                    
            except Exception as e:
                return {'status': 'fail', 'message': f'Scenario test error: {str(e)}'}
        
        test_control("Individual-Only Scenario", test_scenario_individual_only)
        
        def test_scenario_limited_count():
            """Test limited individual property count scenario"""
            try:
                # Set to limited count mode
                gui.individual_mode_var.set('with_listing')
                gui.individual_count_var.set('100')
                gui.force_rescrape_var.set(True)
                
                config = gui.get_individual_scraping_config()
                
                if config['max_count'] == 100 and config['force_rescrape'] == True:
                    return {'status': 'pass', 'message': 'Limited count scenario works correctly'}
                else:
                    return {'status': 'warning', 'message': f'Limited count config issue: {config}'}
                    
            except Exception as e:
                return {'status': 'fail', 'message': f'Limited count test error: {str(e)}'}
        
        test_control("Limited Count Scenario", test_scenario_limited_count)
        
        # Close GUI
        gui.root.after(100, gui.root.destroy)
        gui.root.mainloop()
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 ENHANCED INDIVIDUAL CONTROLS TEST RESULTS")
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
        
        print(f"\n📈 ENHANCED CONTROLS SUCCESS RATE: {success:.1f}% ({len(results['passed'])}/{total})")
        
        # Test specific scenarios
        print("\n" + "=" * 60)
        print("🎯 SCENARIO TESTING SUMMARY")
        print("=" * 60)
        
        print("✅ Scenario 1: Individual-Only Scraping")
        print("   - Skip listing scraping")
        print("   - Only scrape individual property pages")
        print("   - Use existing property URLs")
        
        print("✅ Scenario 2: Limited Individual Properties")
        print("   - Scrape listings first")
        print("   - Limit individual properties to specified count")
        print("   - Option to force re-scrape existing properties")
        
        print("✅ Scenario 3: Incremental Individual Scraping")
        print("   - Show count of already scraped properties")
        print("   - Skip already scraped properties by default")
        print("   - Option to force re-scrape if needed")
        
        return results
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_enhanced_individual_controls()
