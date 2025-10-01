#!/usr/bin/env python3
"""
Test script to verify GUI scrolling functionality
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add current directory to path to import GUI
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gui_scrolling():
    """Test the GUI scrolling functionality"""
    
    print("🧪 Testing MagicBricks GUI Scrolling...")
    
    try:
        # Import the GUI class
        from magicbricks_gui import MagicBricksGUI
        
        print("✅ GUI module imported successfully")
        
        # Create GUI instance
        gui = MagicBricksGUI()
        
        print("✅ GUI instance created successfully")
        
        # Add a test method to check scrolling
        def check_scrolling():
            """Check if scrolling is working"""
            try:
                if hasattr(gui, 'scrollable_panel'):
                    scrollable_frame = gui.scrollable_panel.get_frame()
                    children = scrollable_frame.winfo_children()
                    
                    print(f"✅ Scrollable frame has {len(children)} child widgets")
                    
                    # List all sections found
                    sections = []
                    for child in children:
                        if isinstance(child, ttk.LabelFrame):
                            sections.append(child.cget('text'))
                    
                    print(f"📋 Found sections: {sections}")
                    
                    # Check if all expected sections are present
                    expected_sections = [
                        "🏙️ City Selection",
                        "⚙️ Scraping Mode", 
                        "📊 Basic Settings",
                        "🔧 Advanced Options",
                        "💾 Export Options",
                        "⏱️ Timing & Performance",
                        "⚡ Performance Settings",
                        "🌐 Browser Speed Settings",
                        "🔍 Property Filtering",
                        "[TARGET] Actions"
                    ]
                    
                    missing_sections = []
                    for expected in expected_sections:
                        found = False
                        for section in sections:
                            if expected.replace("🔧", "[SETUP]").replace("💾", "[SAVE]") in section or expected in section:
                                found = True
                                break
                        if not found:
                            missing_sections.append(expected)
                    
                    if missing_sections:
                        print(f"⚠️ Missing sections: {missing_sections}")
                    else:
                        print("✅ All expected sections found!")
                    
                    # Test scrolling functionality
                    canvas = gui.scrollable_panel.canvas
                    scrollregion = canvas.cget('scrollregion')
                    print(f"📏 Scroll region: {scrollregion}")
                    
                    if scrollregion and scrollregion != "0 0 0 0":
                        print("✅ Scrolling is properly configured")
                    else:
                        print("⚠️ Scrolling may not be working properly")
                    
                else:
                    print("❌ Scrollable panel not found")
                    
            except Exception as e:
                print(f"❌ Error checking scrolling: {e}")
        
        # Schedule the check after GUI is fully loaded
        gui.root.after(1000, check_scrolling)
        
        # Add a close button for testing
        def close_test():
            print("🏁 Test completed")
            gui.root.destroy()
        
        gui.root.after(5000, close_test)  # Auto-close after 5 seconds
        
        print("🚀 Starting GUI test...")
        gui.root.mainloop()
        
        print("✅ GUI test completed successfully")
        
    except Exception as e:
        print(f"❌ Error testing GUI: {e}")
        import traceback
        traceback.print_exc()

def test_scrollable_frame_standalone():
    """Test the scrollable frame implementation standalone"""
    
    print("🧪 Testing Scrollable Frame Standalone...")
    
    root = tk.Tk()
    root.title("Scrollable Frame Test")
    root.geometry("600x400")
    
    # Import the scrollable frame from our fix
    from gui_scrolling_fix import ScrollableFrame
    
    # Create scrollable frame
    scrollable = ScrollableFrame(root)
    scrollable.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # Get the frame to add content to
    content_frame = scrollable.get_frame()
    
    # Add lots of content to test scrolling
    for i in range(50):
        section = ttk.LabelFrame(content_frame, text=f"Section {i+1}", padding="10")
        section.pack(fill=tk.X, pady=5)
        
        for j in range(3):
            ttk.Label(section, text=f"Label {j+1} in section {i+1}").pack(anchor=tk.W)
            ttk.Button(section, text=f"Button {j+1}").pack(anchor=tk.W, pady=2)
    
    print("✅ Scrollable frame test created")
    print("🖱️ Try scrolling with mouse wheel")
    
    # Auto-close after 10 seconds
    root.after(10000, root.destroy)
    
    root.mainloop()
    print("✅ Standalone scrollable frame test completed")

if __name__ == "__main__":
    print("🔧 MagicBricks GUI Scrolling Test Suite")
    print("=" * 50)
    
    # Test 1: Standalone scrollable frame
    test_scrollable_frame_standalone()
    
    print("\n" + "=" * 50)
    
    # Test 2: Full GUI scrolling
    test_gui_scrolling()
    
    print("\n🎉 All tests completed!")
