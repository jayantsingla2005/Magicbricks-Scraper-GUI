#!/usr/bin/env python3
"""
Test GUI Components
Simple test to verify GUI components work properly
"""

import tkinter as tk
from tkinter import ttk
import sys

def test_gui_components():
    """Test basic GUI components"""
    
    print("🧪 Testing GUI Components...")
    
    try:
        # Test basic tkinter
        root = tk.Tk()
        root.title("GUI Test")
        root.geometry("400x300")
        
        # Test ttk components
        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Test label
        label = ttk.Label(frame, text="GUI Test Successful!", font=('Arial', 14, 'bold'))
        label.pack(pady=10)
        
        # Test combobox
        combo = ttk.Combobox(frame, values=['Option 1', 'Option 2', 'Option 3'])
        combo.pack(pady=5)
        combo.set('Option 1')
        
        # Test button
        def on_click():
            print("✅ Button clicked successfully!")
            root.quit()
        
        button = ttk.Button(frame, text="Test Button", command=on_click)
        button.pack(pady=10)
        
        # Test progressbar
        progress = ttk.Progressbar(frame, length=200, mode='determinate')
        progress.pack(pady=5)
        progress['value'] = 50
        
        # Test text widget
        text = tk.Text(frame, height=5, width=40)
        text.pack(pady=5)
        text.insert(tk.END, "GUI components working correctly!\n")
        text.insert(tk.END, "✅ tkinter: OK\n")
        text.insert(tk.END, "✅ ttk: OK\n")
        text.insert(tk.END, "✅ All components: OK\n")
        
        print("✅ GUI components initialized successfully")
        print("📋 GUI window should be visible")
        print("🔘 Click the 'Test Button' to close")
        
        # Auto-close after 3 seconds for automated testing
        root.after(3000, lambda: (print("⏰ Auto-closing GUI test"), root.quit()))
        
        # Start GUI
        root.mainloop()
        root.destroy()
        
        print("✅ GUI test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {str(e)}")
        return False

def test_imports():
    """Test required imports"""
    
    print("🧪 Testing Required Imports...")
    
    try:
        import tkinter as tk
        print("✅ tkinter: OK")
        
        from tkinter import ttk, messagebox, filedialog, scrolledtext
        print("✅ tkinter.ttk: OK")
        print("✅ tkinter.messagebox: OK")
        print("✅ tkinter.filedialog: OK")
        print("✅ tkinter.scrolledtext: OK")
        
        import threading
        print("✅ threading: OK")
        
        import queue
        print("✅ queue: OK")
        
        import json
        print("✅ json: OK")
        
        from datetime import datetime
        print("✅ datetime: OK")
        
        from pathlib import Path
        print("✅ pathlib: OK")
        
        print("✅ All required imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def main():
    """Main test function"""
    
    print("🚀 STARTING GUI COMPONENT TESTS")
    print("="*50)
    
    # Test imports
    imports_ok = test_imports()
    
    if not imports_ok:
        print("❌ Import tests failed - cannot proceed with GUI tests")
        return False
    
    print("\n" + "="*50)
    
    # Test GUI components
    gui_ok = test_gui_components()
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS:")
    print(f"✅ Imports: {'PASS' if imports_ok else 'FAIL'}")
    print(f"✅ GUI Components: {'PASS' if gui_ok else 'FAIL'}")
    
    if imports_ok and gui_ok:
        print("🎉 ALL TESTS PASSED - GUI READY FOR DEVELOPMENT")
        return True
    else:
        print("❌ SOME TESTS FAILED - CHECK ENVIRONMENT")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
