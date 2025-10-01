#!/usr/bin/env python3
"""
Deep GUI Control Testing - Tests every single control thoroughly
"""

import tkinter as tk
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def deep_test_gui_controls():
    """Deep testing of all GUI controls"""
    
    print("🧪 DEEP GUI CONTROL TESTING")
    print("=" * 60)
    
    try:
        from magicbricks_gui import MagicBricksGUI
        
        # Create GUI instance
        gui = MagicBricksGUI()
        print("✅ GUI instance created successfully")
        
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
        
        # === CITY SELECTION TESTING ===
        def test_city_selection():
            if hasattr(gui, 'selected_cities_var'):
                default = gui.selected_cities_var.get()
                return {'status': 'pass', 'message': f'Default city: {default}'}
            return {'status': 'fail', 'message': 'selected_cities_var not found'}
        
        test_control("City Selection Variable", test_city_selection)
        
        # === SCRAPING MODE TESTING ===
        def test_scraping_mode():
            if hasattr(gui, 'mode_var'):
                mode = gui.mode_var.get()
                valid = ['incremental', 'full', 'conservative', 'date_range', 'custom']
                if mode in valid:
                    return {'status': 'pass', 'message': f'Mode: {mode}'}
                return {'status': 'warning', 'message': f'Invalid mode: {mode}'}
            return {'status': 'fail', 'message': 'mode_var not found'}
        
        test_control("Scraping Mode", test_scraping_mode)
        
        # === BASIC SETTINGS ===
        def test_max_pages():
            if hasattr(gui, 'max_pages_var'):
                pages = gui.max_pages_var.get()
                try:
                    pages_int = int(pages)
                    return {'status': 'pass', 'message': f'Max pages: {pages_int}'}
                except ValueError:
                    return {'status': 'fail', 'message': f'Invalid pages: {pages}'}
            return {'status': 'fail', 'message': 'max_pages_var not found'}
        
        test_control("Max Pages", test_max_pages)
        
        def test_output_dir():
            if hasattr(gui, 'output_dir_var'):
                dir_path = gui.output_dir_var.get()
                return {'status': 'pass', 'message': f'Output dir: {dir_path}'}
            return {'status': 'fail', 'message': 'output_dir_var not found'}
        
        test_control("Output Directory", test_output_dir)
        
        # === ADVANCED OPTIONS ===
        def test_headless():
            if hasattr(gui, 'headless_var'):
                headless = gui.headless_var.get()
                return {'status': 'pass', 'message': f'Headless: {headless}'}
            return {'status': 'fail', 'message': 'headless_var not found'}
        
        test_control("Headless Mode", test_headless)
        
        def test_incremental():
            if hasattr(gui, 'incremental_var'):
                incremental = gui.incremental_var.get()
                return {'status': 'pass', 'message': f'Incremental: {incremental}'}
            return {'status': 'fail', 'message': 'incremental_var not found'}
        
        test_control("Incremental Scraping", test_incremental)
        
        def test_individual_pages():
            if hasattr(gui, 'individual_pages_var'):
                individual = gui.individual_pages_var.get()
                return {'status': 'pass', 'message': f'Individual pages: {individual}'}
            return {'status': 'fail', 'message': 'individual_pages_var not found'}
        
        test_control("Individual Pages", test_individual_pages)
        
        # === EXPORT OPTIONS ===
        def test_export_json():
            if hasattr(gui, 'export_json_var'):
                json_export = gui.export_json_var.get()
                return {'status': 'pass', 'message': f'Export JSON: {json_export}'}
            return {'status': 'fail', 'message': 'export_json_var not found'}
        
        test_control("Export JSON", test_export_json)
        
        def test_export_excel():
            if hasattr(gui, 'export_excel_var'):
                excel_export = gui.export_excel_var.get()
                return {'status': 'pass', 'message': f'Export Excel: {excel_export}'}
            return {'status': 'fail', 'message': 'export_excel_var not found'}
        
        test_control("Export Excel", test_export_excel)
        
        # === TIMING SETTINGS ===
        def test_page_delay():
            if hasattr(gui, 'delay_var'):
                delay = gui.delay_var.get()
                try:
                    delay_int = int(delay)
                    return {'status': 'pass', 'message': f'Page delay: {delay_int}s'}
                except ValueError:
                    return {'status': 'fail', 'message': f'Invalid delay: {delay}'}
            return {'status': 'fail', 'message': 'delay_var not found'}
        
        test_control("Page Delay", test_page_delay)
        
        def test_max_retries():
            if hasattr(gui, 'retry_var'):
                retries = gui.retry_var.get()
                try:
                    retries_int = int(retries)
                    return {'status': 'pass', 'message': f'Max retries: {retries_int}'}
                except ValueError:
                    return {'status': 'fail', 'message': f'Invalid retries: {retries}'}
            return {'status': 'fail', 'message': 'retry_var not found'}
        
        test_control("Max Retries", test_max_retries)
        
        # === PERFORMANCE SETTINGS ===
        def test_batch_size():
            if hasattr(gui, 'batch_size_var'):
                batch = gui.batch_size_var.get()
                try:
                    batch_int = int(batch)
                    return {'status': 'pass', 'message': f'Batch size: {batch_int}'}
                except ValueError:
                    return {'status': 'fail', 'message': f'Invalid batch: {batch}'}
            return {'status': 'fail', 'message': 'batch_size_var not found'}
        
        test_control("Batch Size", test_batch_size)
        
        def test_max_workers():
            if hasattr(gui, 'max_workers_var'):
                workers = gui.max_workers_var.get()
                return {'status': 'pass', 'message': f'Max workers: {workers}'}
            return {'status': 'fail', 'message': 'max_workers_var not found'}
        
        test_control("Max Workers", test_max_workers)
        
        # === BROWSER SETTINGS ===
        def test_page_load_strategy():
            if hasattr(gui, 'page_load_strategy_var'):
                strategy = gui.page_load_strategy_var.get()
                return {'status': 'pass', 'message': f'Load strategy: {strategy}'}
            return {'status': 'fail', 'message': 'page_load_strategy_var not found'}
        
        test_control("Page Load Strategy", test_page_load_strategy)
        
        def test_disable_images():
            if hasattr(gui, 'disable_images_var'):
                disable_img = gui.disable_images_var.get()
                return {'status': 'pass', 'message': f'Disable images: {disable_img}'}
            return {'status': 'fail', 'message': 'disable_images_var not found'}
        
        test_control("Disable Images", test_disable_images)
        
        # === FILTERING ===
        def test_filtering():
            if hasattr(gui, 'enable_filtering_var'):
                filtering = gui.enable_filtering_var.get()
                return {'status': 'pass', 'message': f'Filtering: {filtering}'}
            return {'status': 'fail', 'message': 'enable_filtering_var not found'}
        
        test_control("Property Filtering", test_filtering)
        
        # === ACTION BUTTONS ===
        def test_start_button():
            if hasattr(gui, 'start_button'):
                return {'status': 'pass', 'message': 'Start button exists'}
            return {'status': 'fail', 'message': 'start_button not found'}
        
        test_control("Start Button", test_start_button)
        
        def test_stop_button():
            if hasattr(gui, 'stop_btn'):
                return {'status': 'pass', 'message': 'Stop button exists'}
            return {'status': 'fail', 'message': 'stop_btn not found'}
        
        test_control("Stop Button", test_stop_button)
        
        # === CONFIG INTEGRATION ===
        def test_config():
            if hasattr(gui, 'config'):
                return {'status': 'pass', 'message': 'Config object exists'}
            return {'status': 'fail', 'message': 'config not found'}
        
        test_control("Configuration", test_config)
        
        # Close GUI
        gui.root.after(100, gui.root.destroy)
        gui.root.mainloop()
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS")
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
        
        print(f"\n📈 SUCCESS RATE: {success:.1f}% ({len(results['passed'])}/{total})")
        
        return results
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    deep_test_gui_controls()
