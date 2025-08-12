#!/usr/bin/env python3
"""
Comprehensive GUI Testing Suite for MagicBricks Property Scraper
Tests all GUI components, functionality, and visual elements
"""

import tkinter as tk
import sys
import os
from pathlib import Path
import time
import threading

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

class GUITester:
    def __init__(self):
        self.test_results = []
        self.gui_app = None
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': time.strftime('%H:%M:%S')
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status} {details}")
    
    def test_imports(self):
        """Test if all required modules can be imported"""
        print("\n🔍 Testing Module Imports...")
        
        try:
            import tkinter as tk
            from tkinter import ttk
            self.log_test("Tkinter Import", "PASS", "Core GUI library available")
        except ImportError as e:
            self.log_test("Tkinter Import", "FAIL", str(e))
            return False
            
        try:
            from magicbricks_gui import MagicBricksGUI
            self.log_test("MagicBricks GUI Import", "PASS", "Main GUI class available")
        except ImportError as e:
            self.log_test("MagicBricks GUI Import", "FAIL", str(e))
            return False
            
        try:
            from multi_city_system import MultiCitySystem
            self.log_test("Multi-City System Import", "PASS", "City management available")
        except ImportError as e:
            self.log_test("Multi-City System Import", "FAIL", str(e))
            
        try:
            from error_handling_system import ErrorHandlingSystem
            self.log_test("Error Handling Import", "PASS", "Error management available")
        except ImportError as e:
            self.log_test("Error Handling Import", "FAIL", str(e))
            
        return True
    
    def test_gui_initialization(self):
        """Test GUI initialization without showing window"""
        print("\n🎨 Testing GUI Initialization...")
        
        try:
            # Import the GUI class
            from magicbricks_gui import MagicBricksGUI
            
            # Create GUI instance (but don't show it)
            self.gui_app = MagicBricksGUI()
            self.log_test("GUI Object Creation", "PASS", "GUI instance created successfully")
            
            # Test if root window exists
            if hasattr(self.gui_app, 'root') and self.gui_app.root:
                self.log_test("Root Window Creation", "PASS", "Main window object exists")
            else:
                self.log_test("Root Window Creation", "FAIL", "No root window found")
                
            # Test style configuration
            if hasattr(self.gui_app, 'style') and self.gui_app.style:
                self.log_test("Style System", "PASS", "TTK styling configured")
            else:
                self.log_test("Style System", "FAIL", "No style system found")
                
            # Test color palette
            if hasattr(self.gui_app, 'colors') and self.gui_app.colors:
                color_count = len(self.gui_app.colors)
                self.log_test("Color Palette", "PASS", f"{color_count} colors defined")
            else:
                self.log_test("Color Palette", "FAIL", "No color palette found")
                
            return True
            
        except Exception as e:
            self.log_test("GUI Initialization", "FAIL", str(e))
            return False
    
    def test_gui_components(self):
        """Test individual GUI components"""
        print("\n🔧 Testing GUI Components...")
        
        if not self.gui_app:
            self.log_test("Component Testing", "SKIP", "No GUI instance available")
            return False
            
        # Test configuration object
        if hasattr(self.gui_app, 'config') and self.gui_app.config:
            config_keys = len(self.gui_app.config.keys())
            self.log_test("Configuration System", "PASS", f"{config_keys} config options")
        else:
            self.log_test("Configuration System", "FAIL", "No configuration found")
            
        # Test city system
        if hasattr(self.gui_app, 'city_system') and self.gui_app.city_system:
            try:
                city_count = len(self.gui_app.city_system.cities)
                self.log_test("City System", "PASS", f"{city_count} cities available")
            except:
                self.log_test("City System", "WARN", "City system exists but cities not accessible")
        else:
            self.log_test("City System", "FAIL", "No city system found")
            
        # Test error handling system
        if hasattr(self.gui_app, 'error_system') and self.gui_app.error_system:
            self.log_test("Error Handling", "PASS", "Error system initialized")
        else:
            self.log_test("Error Handling", "FAIL", "No error handling system")
            
        # Test message queue
        if hasattr(self.gui_app, 'message_queue') and self.gui_app.message_queue:
            self.log_test("Message Queue", "PASS", "Inter-thread communication ready")
        else:
            self.log_test("Message Queue", "FAIL", "No message queue found")
            
        return True
    
    def test_visual_elements(self):
        """Test visual styling and modern elements"""
        print("\n🎨 Testing Visual Elements...")
        
        if not self.gui_app:
            self.log_test("Visual Testing", "SKIP", "No GUI instance available")
            return False
            
        # Test modern styles
        try:
            style = self.gui_app.style
            
            # Check for modern button styles
            button_styles = ['Primary.TButton', 'Secondary.TButton', 'Success.TButton', 'Danger.TButton']
            for btn_style in button_styles:
                try:
                    style.configure(btn_style)
                    self.log_test(f"Button Style: {btn_style}", "PASS", "Style configured")
                except:
                    self.log_test(f"Button Style: {btn_style}", "FAIL", "Style not found")
                    
            # Check for modern label styles
            label_styles = ['Title.TLabel', 'Heading.TLabel', 'Info.TLabel']
            for lbl_style in label_styles:
                try:
                    style.configure(lbl_style)
                    self.log_test(f"Label Style: {lbl_style}", "PASS", "Style configured")
                except:
                    self.log_test(f"Label Style: {lbl_style}", "FAIL", "Style not found")
                    
            # Check for modern frame styles
            frame_styles = ['Card.TFrame', 'Modern.TLabelframe']
            for frm_style in frame_styles:
                try:
                    style.configure(frm_style)
                    self.log_test(f"Frame Style: {frm_style}", "PASS", "Style configured")
                except:
                    self.log_test(f"Frame Style: {frm_style}", "FAIL", "Style not found")
                    
        except Exception as e:
            self.log_test("Visual Elements", "FAIL", str(e))
            
        return True
    
    def test_window_properties(self):
        """Test window configuration and properties"""
        print("\n🪟 Testing Window Properties...")
        
        if not self.gui_app or not self.gui_app.root:
            self.log_test("Window Testing", "SKIP", "No window available")
            return False
            
        root = self.gui_app.root
        
        # Test window title
        title = root.title()
        if "MagicBricks" in title and "Professional Edition" in title:
            self.log_test("Window Title", "PASS", f"Title: {title[:50]}...")
        else:
            self.log_test("Window Title", "WARN", f"Unexpected title: {title}")
            
        # Test window geometry
        geometry = root.geometry()
        if "1450x950" in geometry or "1400x900" in geometry:
            self.log_test("Window Size", "PASS", f"Geometry: {geometry}")
        else:
            self.log_test("Window Size", "WARN", f"Unexpected size: {geometry}")
            
        # Test minimum size
        try:
            min_width = root.minsize()[0]
            min_height = root.minsize()[1]
            if min_width >= 1200 and min_height >= 700:
                self.log_test("Minimum Size", "PASS", f"Min: {min_width}x{min_height}")
            else:
                self.log_test("Minimum Size", "WARN", f"Small min size: {min_width}x{min_height}")
        except:
            self.log_test("Minimum Size", "FAIL", "Could not get minimum size")
            
        return True
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE GUI TEST REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warned_tests = len([t for t in self.test_results if t['status'] == 'WARN'])
        skipped_tests = len([t for t in self.test_results if t['status'] == 'SKIP'])
        
        print(f"\n📈 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️  Warnings: {warned_tests}")
        print(f"   ⏭️  Skipped: {skipped_tests}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"   🎯 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for test in self.test_results:
                if test['status'] == 'FAIL':
                    print(f"   • {test['test']}: {test['details']}")
                    
        if warned_tests > 0:
            print(f"\n⚠️  Warnings:")
            for test in self.test_results:
                if test['status'] == 'WARN':
                    print(f"   • {test['test']}: {test['details']}")
        
        print(f"\n🎨 GUI Status:")
        if success_rate >= 90:
            print("   🟢 EXCELLENT - GUI is fully functional with modern styling")
        elif success_rate >= 75:
            print("   🟡 GOOD - GUI is functional with minor issues")
        elif success_rate >= 50:
            print("   🟠 FAIR - GUI has some functionality but needs attention")
        else:
            print("   🔴 POOR - GUI has significant issues that need fixing")
            
        print("\n" + "="*60)
        
        return success_rate
    
    def run_all_tests(self):
        """Run all GUI tests"""
        print("🚀 Starting Comprehensive GUI Testing Suite")
        print("Testing MagicBricks Property Scraper GUI v2.0")
        print("-" * 60)
        
        # Run all test suites
        self.test_imports()
        self.test_gui_initialization()
        self.test_gui_components()
        self.test_visual_elements()
        self.test_window_properties()
        
        # Generate final report
        success_rate = self.generate_report()
        
        # Cleanup
        if self.gui_app and self.gui_app.root:
            try:
                self.gui_app.root.destroy()
            except:
                pass
                
        return success_rate

def main():
    """Main testing function"""
    print("🏠 MagicBricks GUI Comprehensive Testing Suite")
    print("=" * 50)
    
    tester = GUITester()
    success_rate = tester.run_all_tests()
    
    print(f"\n🏁 Testing Complete! Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 Your GUI is ready for production use!")
    elif success_rate >= 75:
        print("👍 Your GUI is in good shape with minor improvements needed.")
    else:
        print("🔧 Your GUI needs some attention before production use.")
        
    return success_rate

if __name__ == "__main__":
    main()