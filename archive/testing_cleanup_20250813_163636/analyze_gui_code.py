#!/usr/bin/env python3
"""
Analyze the GUI code structure to understand why it's so large
"""

import re


def analyze_gui_code():
    """Analyze the GUI code structure"""
    
    print("🔍 GUI CODE ANALYSIS")
    print("=" * 50)
    
    # Read the GUI file
    with open('magicbricks_gui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    total_lines = len(lines)
    
    print(f"Total lines: {total_lines}")
    print()
    
    # Count methods
    methods = re.findall(r'def (\w+)\(', content)
    print(f"Total methods: {len(methods)}")
    print()
    
    # Analyze method sizes
    method_sizes = {}
    current_method = None
    current_size = 0
    
    for line in lines:
        if line.strip().startswith('def '):
            if current_method:
                method_sizes[current_method] = current_size
            current_method = re.search(r'def (\w+)\(', line)
            if current_method:
                current_method = current_method.group(1)
                current_size = 1
        elif current_method and line.strip():
            current_size += 1
    
    # Add last method
    if current_method:
        method_sizes[current_method] = current_size
    
    # Find largest methods
    largest_methods = sorted(method_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print("📊 LARGEST METHODS:")
    for method, size in largest_methods:
        print(f"   {method}: {size} lines")
    
    print()
    
    # Count different types of code
    ui_creation_lines = len([l for l in lines if any(keyword in l for keyword in ['ttk.', 'tk.', '.pack(', '.grid(', '.place('])])
    style_lines = len([l for l in lines if 'style.configure' in l or 'style.map' in l])
    callback_lines = len([l for l in lines if 'callback' in l or 'command=' in l])
    comment_lines = len([l for l in lines if l.strip().startswith('#')])
    empty_lines = len([l for l in lines if not l.strip()])
    
    print("📈 CODE BREAKDOWN:")
    print(f"   UI Creation: {ui_creation_lines} lines ({ui_creation_lines/total_lines*100:.1f}%)")
    print(f"   Styling: {style_lines} lines ({style_lines/total_lines*100:.1f}%)")
    print(f"   Callbacks: {callback_lines} lines ({callback_lines/total_lines*100:.1f}%)")
    print(f"   Comments: {comment_lines} lines ({comment_lines/total_lines*100:.1f}%)")
    print(f"   Empty lines: {empty_lines} lines ({empty_lines/total_lines*100:.1f}%)")
    print(f"   Actual code: {total_lines - comment_lines - empty_lines} lines ({(total_lines - comment_lines - empty_lines)/total_lines*100:.1f}%)")
    
    print()
    
    # Identify refactoring opportunities
    print("🔧 REFACTORING OPPORTUNITIES:")
    
    # Large methods that can be broken down
    large_methods = [method for method, size in method_sizes.items() if size > 50]
    print(f"   Methods > 50 lines: {len(large_methods)}")
    for method in large_methods[:5]:
        print(f"     - {method}: {method_sizes[method]} lines")
    
    # Repetitive patterns
    widget_creation_patterns = [
        'ttk.Label',
        'ttk.Button', 
        'ttk.Frame',
        'ttk.LabelFrame',
        'ttk.Entry',
        'ttk.Combobox'
    ]
    
    print(f"   Widget creation instances:")
    for pattern in widget_creation_patterns:
        count = len([l for l in lines if pattern in l])
        print(f"     - {pattern}: {count} instances")
    
    print()
    
    # Suggest modular structure
    print("🏗️ SUGGESTED MODULAR STRUCTURE:")
    print("   1. StyleManager - Handle all styling (current: ~300 lines)")
    print("   2. LayoutManager - Handle layout creation (~500 lines)")
    print("   3. ConfigurationPanel - City/settings panel (~200 lines)")
    print("   4. MonitoringPanel - Progress/stats panel (~300 lines)")
    print("   5. ResultsPanel - Results display (~200 lines)")
    print("   6. EventHandlers - All callbacks (~400 lines)")
    print("   7. DataManager - Data handling (~300 lines)")
    print("   8. MainGUI - Orchestration (~200 lines)")
    print()
    print(f"   Estimated reduction: {total_lines} → ~2400 lines (23% reduction)")
    print("   Benefits: Better maintainability, easier testing, clearer separation")


if __name__ == "__main__":
    analyze_gui_code()
