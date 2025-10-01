#!/usr/bin/env python3
"""
Manual GUI Control Testing - Test every control with real values
"""

import tkinter as tk
import sys
import os
import time
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def manual_test_all_controls():
    """Manually test all GUI controls with real value changes"""
    
    print("🔧 MANUAL GUI CONTROL TESTING")
    print("=" * 60)
    
    try:
        from magicbricks_gui import MagicBricksGUI
        
        # Create GUI instance
        gui = MagicBricksGUI()
        print("✅ GUI instance created")
        
        # Test results
        test_results = []
        
        def test_control_manipulation(control_name, test_func):
            """Test manipulating a control and verify it works"""
            try:
                result = test_func()
                if result:
                    test_results.append(f"✅ {control_name}: {result}")
                    print(f"✅ {control_name}: {result}")
                else:
                    test_results.append(f"❌ {control_name}: Failed")
                    print(f"❌ {control_name}: Failed")
            except Exception as e:
                test_results.append(f"❌ {control_name}: Exception - {str(e)}")
                print(f"❌ {control_name}: Exception - {str(e)}")
        
        # Wait for GUI to fully load
        time.sleep(1)
        
        # === TEST CITY SELECTION ===
        def test_city_selection():
            original = gui.selected_cities_var.get()
            gui.selected_cities_var.set("mumbai")
            new_value = gui.selected_cities_var.get()
            gui.selected_cities_var.set(original)  # Reset
            return f"Changed from '{original}' to '{new_value}'"
        
        test_control_manipulation("City Selection", test_city_selection)
        
        # === TEST SCRAPING MODE ===
        def test_scraping_mode():
            original = gui.mode_var.get()
            gui.mode_var.set("full")
            new_value = gui.mode_var.get()
            gui.mode_var.set(original)  # Reset
            return f"Changed from '{original}' to '{new_value}'"
        
        test_control_manipulation("Scraping Mode", test_scraping_mode)
        
        # === TEST MAX PAGES ===
        def test_max_pages():
            original = gui.max_pages_var.get()
            gui.max_pages_var.set("50")
            new_value = gui.max_pages_var.get()
            gui.max_pages_var.set(original)  # Reset
            return f"Changed from '{original}' to '{new_value}'"
        
        test_control_manipulation("Max Pages", test_max_pages)
        
        # === TEST OUTPUT DIRECTORY ===
        def test_output_directory():
            original = gui.output_dir_var.get()
            test_dir = "D:/test_output"
            gui.output_dir_var.set(test_dir)
            new_value = gui.output_dir_var.get()
            gui.output_dir_var.set(original)  # Reset
            return f"Changed from '{original}' to '{new_value}'"
        
        test_control_manipulation("Output Directory", test_output_directory)
        
        # === TEST HEADLESS MODE ===
        def test_headless_mode():
            original = gui.headless_var.get()
            gui.headless_var.set(not original)
            new_value = gui.headless_var.get()
            gui.headless_var.set(original)  # Reset
            return f"Toggled from {original} to {new_value}"
        
        test_control_manipulation("Headless Mode", test_headless_mode)
        
        # === TEST INCREMENTAL SCRAPING ===
        def test_incremental_scraping():
            original = gui.incremental_var.get()
            gui.incremental_var.set(not original)
            new_value = gui.incremental_var.get()
            gui.incremental_var.set(original)  # Reset
            return f"Toggled from {original} to {new_value}"
        
        test_control_manipulation("Incremental Scraping", test_incremental_scraping)
        
        # === TEST INDIVIDUAL PAGES ===
        def test_individual_pages():
            original = gui.individual_pages_var.get()
            gui.individual_pages_var.set(not original)
            new_value = gui.individual_pages_var.get()
            gui.individual_pages_var.set(original)  # Reset
            return f"Toggled from {original} to {new_value}"
        
        test_control_manipulation("Individual Pages", test_individual_pages)
        
        # === TEST EXPORT OPTIONS ===
        def test_export_json():
            original = gui.export_json_var.get()
            gui.export_json_var.set(not original)
            new_value = gui.export_json_var.get()
            gui.export_json_var.set(original)  # Reset
            return f"Toggled JSON export from {original} to {new_value}"
        
        test_control_manipulation("Export JSON", test_export_json)
        
        def test_export_excel():
            original = gui.export_excel_var.get()
            gui.export_excel_var.set(not original)
            new_value = gui.export_excel_var.get()
            gui.export_excel_var.set(original)  # Reset
            return f"Toggled Excel export from {original} to {new_value}"
        
        test_control_manipulation("Export Excel", test_export_excel)
        
        # === TEST TIMING SETTINGS ===
        def test_page_delay():
            original = gui.delay_var.get()
            gui.delay_var.set("5")
            new_value = gui.delay_var.get()
            gui.delay_var.set(original)  # Reset
            return f"Changed page delay from {original} to {new_value}"
        
        test_control_manipulation("Page Delay", test_page_delay)
        
        def test_max_retries():
            original = gui.retry_var.get()
            gui.retry_var.set("5")
            new_value = gui.retry_var.get()
            gui.retry_var.set(original)  # Reset
            return f"Changed max retries from {original} to {new_value}"
        
        test_control_manipulation("Max Retries", test_max_retries)
        
        # === TEST PERFORMANCE SETTINGS ===
        def test_batch_size():
            original = gui.batch_size_var.get()
            gui.batch_size_var.set("20")
            new_value = gui.batch_size_var.get()
            gui.batch_size_var.set(original)  # Reset
            return f"Changed batch size from {original} to {new_value}"
        
        test_control_manipulation("Batch Size", test_batch_size)
        
        def test_max_workers():
            original = gui.max_workers_var.get()
            gui.max_workers_var.set(5)
            new_value = gui.max_workers_var.get()
            gui.max_workers_var.set(original)  # Reset
            return f"Changed max workers from {original} to {new_value}"
        
        test_control_manipulation("Max Workers", test_max_workers)
        
        # === TEST ENHANCED INDIVIDUAL PROPERTY CONTROLS ===
        def test_individual_mode():
            original = gui.individual_mode_var.get()
            gui.individual_mode_var.set("individual_only")
            new_value = gui.individual_mode_var.get()
            gui.individual_mode_var.set(original)  # Reset
            return f"Changed individual mode from '{original}' to '{new_value}'"
        
        test_control_manipulation("Individual Scraping Mode", test_individual_mode)
        
        def test_individual_count():
            original = gui.individual_count_var.get()
            gui.individual_count_var.set("50")
            new_value = gui.individual_count_var.get()
            gui.individual_count_var.set(original)  # Reset
            return f"Changed individual count from {original} to {new_value}"
        
        test_control_manipulation("Individual Property Count", test_individual_count)
        
        def test_force_rescrape():
            original = gui.force_rescrape_var.get()
            gui.force_rescrape_var.set(not original)
            new_value = gui.force_rescrape_var.get()
            gui.force_rescrape_var.set(original)  # Reset
            return f"Toggled force re-scrape from {original} to {new_value}"
        
        test_control_manipulation("Force Re-scrape", test_force_rescrape)
        
        # === TEST FILTERING CONTROLS ===
        def test_filtering_enabled():
            original = gui.enable_filtering_var.get()
            gui.enable_filtering_var.set(not original)
            new_value = gui.enable_filtering_var.get()
            gui.enable_filtering_var.set(original)  # Reset
            return f"Toggled filtering from {original} to {new_value}"
        
        test_control_manipulation("Property Filtering", test_filtering_enabled)
        
        # === TEST BROWSER SETTINGS ===
        def test_page_load_strategy():
            original = gui.page_load_strategy_var.get()
            gui.page_load_strategy_var.set("eager")
            new_value = gui.page_load_strategy_var.get()
            gui.page_load_strategy_var.set(original)  # Reset
            return f"Changed load strategy from '{original}' to '{new_value}'"
        
        test_control_manipulation("Page Load Strategy", test_page_load_strategy)
        
        def test_disable_images():
            original = gui.disable_images_var.get()
            gui.disable_images_var.set(not original)
            new_value = gui.disable_images_var.get()
            gui.disable_images_var.set(original)  # Reset
            return f"Toggled disable images from {original} to {new_value}"
        
        test_control_manipulation("Disable Images", test_disable_images)
        
        # === TEST CONFIGURATION INTEGRATION ===
        def test_config_integration():
            try:
                # Test getting individual scraping config
                config = gui.get_individual_scraping_config()
                
                # Test refresh scraped count
                gui.refresh_scraped_count()
                count_text = gui.scraped_count_var.get()
                
                return f"Config: {config}, Scraped count: {count_text}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        test_control_manipulation("Configuration Integration", test_config_integration)
        
        # Close GUI after testing
        gui.root.after(100, gui.root.destroy)
        gui.root.mainloop()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 MANUAL CONTROL TESTING SUMMARY")
        print("=" * 60)
        
        passed = len([r for r in test_results if r.startswith("✅")])
        failed = len([r for r in test_results if r.startswith("❌")])
        total = len(test_results)
        
        print(f"\n📈 MANUAL TESTING RESULTS: {passed}/{total} controls working ({passed/total*100:.1f}%)")
        
        if failed > 0:
            print(f"\n❌ FAILED CONTROLS ({failed}):")
            for result in test_results:
                if result.startswith("❌"):
                    print(f"  {result}")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Critical error during manual testing: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = manual_test_all_controls()
    if success:
        print("\n🎉 ALL MANUAL CONTROL TESTS PASSED!")
    else:
        print("\n⚠️ Some manual control tests failed!")
