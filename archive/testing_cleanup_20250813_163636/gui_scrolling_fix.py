#!/usr/bin/env python3
"""
GUI Scrolling Fix for MagicBricks Property Scraper
Comprehensive fix for scrolling and layout issues
"""

import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    """
    A reliable scrollable frame implementation that works better than canvas-based scrolling
    """
    
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel events
        self.bind_mousewheel()
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self.on_canvas_configure)
    
    def bind_mousewheel(self):
        """Bind mouse wheel events for scrolling"""
        
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind when mouse enters the frame
        self.bind('<Enter>', _bind_to_mousewheel)
        self.bind('<Leave>', _unbind_from_mousewheel)
    
    def on_canvas_configure(self, event):
        """Handle canvas resize to adjust scrollable frame width"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def get_frame(self):
        """Get the scrollable frame to add widgets to"""
        return self.scrollable_frame

def create_enhanced_scrollable_control_panel(parent, gui_instance):
    """
    Create enhanced scrollable control panel with reliable scrolling
    """
    
    # Control panel container with modern styling
    control_container = ttk.LabelFrame(parent, text="📋 Scraping Configuration", 
                                     padding="15", style='Modern.TLabelframe')
    control_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
    control_container.columnconfigure(0, weight=1)
    control_container.rowconfigure(0, weight=1)
    
    # Create scrollable frame
    scrollable_panel = ScrollableFrame(control_container)
    scrollable_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Get the frame to add controls to
    controls_frame = scrollable_panel.get_frame()
    controls_frame.columnconfigure(0, weight=1)
    
    # Create all control sections
    create_all_control_sections(controls_frame, gui_instance)
    
    return scrollable_panel

def create_all_control_sections(parent, gui_instance):
    """
    Create all control sections with proper spacing and visibility
    """
    
    parent.columnconfigure(0, weight=1)
    current_row = 0
    
    # Add some top padding
    ttk.Frame(parent, height=10).grid(row=current_row, column=0)
    current_row += 1
    
    # === CITY SELECTION SECTION ===
    current_row = create_city_selection_section(parent, gui_instance, current_row)
    
    # === SCRAPING MODE SECTION ===
    current_row = create_scraping_mode_section(parent, gui_instance, current_row)
    
    # === BASIC SETTINGS SECTION ===
    current_row = create_basic_settings_section(parent, gui_instance, current_row)
    
    # === ADVANCED OPTIONS SECTION ===
    current_row = create_advanced_options_section(parent, gui_instance, current_row)
    
    # === EXPORT OPTIONS SECTION ===
    current_row = create_export_options_section(parent, gui_instance, current_row)
    
    # === TIMING SETTINGS SECTION ===
    current_row = create_timing_settings_section(parent, gui_instance, current_row)
    
    # === PERFORMANCE SECTION ===
    current_row = create_performance_section(parent, gui_instance, current_row)
    
    # === ACTION BUTTONS SECTION ===
    current_row = create_action_buttons_section(parent, gui_instance, current_row)
    
    # Add bottom padding
    ttk.Frame(parent, height=20).grid(row=current_row, column=0)

def create_city_selection_section(parent, gui_instance, current_row):
    """Create city selection section"""
    
    city_section = ttk.LabelFrame(parent, text="🏙️ City Selection", 
                                padding="20", style='Modern.TLabelframe')
    city_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
    city_section.columnconfigure(1, weight=1)
    
    ttk.Label(city_section, text="Selected Cities:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
    
    # Selected cities display
    if not hasattr(gui_instance, 'selected_cities_var'):
        gui_instance.selected_cities_var = tk.StringVar(value="Gurgaon")
    
    cities_frame = ttk.Frame(city_section)
    cities_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
    cities_frame.columnconfigure(0, weight=1)
    
    selected_cities_label = ttk.Label(cities_frame, textvariable=gui_instance.selected_cities_var,
                                    style='Info.TLabel', relief='solid', padding="12")
    selected_cities_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
    
    select_cities_btn = ttk.Button(cities_frame, text="🌍 Select Cities",
                                 command=gui_instance.open_city_selector, style='Secondary.TButton')
    select_cities_btn.grid(row=0, column=1)
    
    return current_row + 1

def create_scraping_mode_section(parent, gui_instance, current_row):
    """Create scraping mode section"""
    
    mode_section = ttk.LabelFrame(parent, text="⚙️ Scraping Mode", 
                                padding="20", style='Modern.TLabelframe')
    mode_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
    mode_section.columnconfigure(1, weight=1)
    
    ttk.Label(mode_section, text="Mode:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
    
    if not hasattr(gui_instance, 'mode_var'):
        gui_instance.mode_var = tk.StringVar(value='incremental')
    
    mode_combo = ttk.Combobox(mode_section, textvariable=gui_instance.mode_var, width=25, 
                            state='readonly', style='Modern.TCombobox')
    mode_combo['values'] = ('incremental', 'full', 'conservative', 'date_range', 'custom')
    mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 15), padx=(15, 0))
    
    # Mode description
    if not hasattr(gui_instance, 'mode_desc_var'):
        gui_instance.mode_desc_var = tk.StringVar(value="Incremental mode: Skip already scraped properties for faster execution")
    
    mode_desc_label = ttk.Label(mode_section, textvariable=gui_instance.mode_desc_var,
                               style='Info.TLabel', wraplength=400)
    mode_desc_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    return current_row + 1

def create_basic_settings_section(parent, gui_instance, current_row):
    """Create basic settings section"""
    
    basic_section = ttk.LabelFrame(parent, text="📊 Basic Settings", 
                                 padding="20", style='Modern.TLabelframe')
    basic_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
    basic_section.columnconfigure(1, weight=1)
    
    # Max pages
    ttk.Label(basic_section, text="📄 Max Pages:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
    
    if not hasattr(gui_instance, 'max_pages_var'):
        gui_instance.max_pages_var = tk.StringVar(value="100")
    
    max_pages_entry = ttk.Entry(basic_section, textvariable=gui_instance.max_pages_var, 
                              width=15, style='Modern.TEntry')
    max_pages_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 15), padx=(15, 0))
    
    # Output directory
    ttk.Label(basic_section, text="📁 Output Directory:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 8))
    
    output_frame = ttk.Frame(basic_section)
    output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 15), padx=(15, 0))
    output_frame.columnconfigure(0, weight=1)
    
    if not hasattr(gui_instance, 'output_dir_var'):
        gui_instance.output_dir_var = tk.StringVar(value="./output")
    
    output_entry = ttk.Entry(output_frame, textvariable=gui_instance.output_dir_var, style='Modern.TEntry')
    output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
    
    browse_btn = ttk.Button(output_frame, text="📂 Browse", 
                          command=lambda: print("Browse directory"), style='Secondary.TButton')
    browse_btn.grid(row=0, column=1)
    
    return current_row + 1

def create_advanced_options_section(parent, gui_instance, current_row):
    """Create advanced options section"""
    
    advanced_section = ttk.LabelFrame(parent, text="🔧 Advanced Options", 
                                    padding="20", style='Modern.TLabelframe')
    advanced_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
    advanced_section.columnconfigure(0, weight=1)
    
    # Checkboxes frame
    checkbox_frame = ttk.Frame(advanced_section)
    checkbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
    checkbox_frame.columnconfigure(0, weight=1)
    checkbox_frame.columnconfigure(1, weight=1)
    
    # Initialize variables if they don't exist
    if not hasattr(gui_instance, 'headless_var'):
        gui_instance.headless_var = tk.BooleanVar(value=True)
    if not hasattr(gui_instance, 'incremental_var'):
        gui_instance.incremental_var = tk.BooleanVar(value=True)
    if not hasattr(gui_instance, 'individual_pages_var'):
        gui_instance.individual_pages_var = tk.BooleanVar(value=False)
    
    # Headless mode
    headless_check = ttk.Checkbutton(checkbox_frame, text="🚀 Headless Mode (faster)",
                                   variable=gui_instance.headless_var)
    headless_check.grid(row=0, column=0, sticky=tk.W, pady=2)
    
    # Incremental enabled
    incremental_check = ttk.Checkbutton(checkbox_frame, text="⚡ Incremental Scraping (60-75% faster)",
                                      variable=gui_instance.incremental_var)
    incremental_check.grid(row=0, column=1, sticky=tk.W, pady=2)
    
    # Individual property pages
    individual_check = ttk.Checkbutton(checkbox_frame, text="📄 Individual Property Details (⚠️ 10x slower)",
                                     variable=gui_instance.individual_pages_var)
    individual_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
    
    # Warning label
    warning_label = ttk.Label(advanced_section, 
                            text="⚠️ Individual property pages will significantly increase scraping time",
                            style='Warning.TLabel', wraplength=400)
    warning_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
    
    return current_row + 1

def create_export_options_section(parent, gui_instance, current_row):
    """Create export options section"""
    
    export_section = ttk.LabelFrame(parent, text="💾 Export Options", 
                                  padding="20", style='Modern.TLabelframe')
    export_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
    export_section.columnconfigure(0, weight=1)
    
    # Mandatory formats
    ttk.Label(export_section, text="✅ Mandatory: CSV + Database",
             style='Success.TLabel', font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
    
    # Optional formats
    optional_frame = ttk.Frame(export_section)
    optional_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
    optional_frame.columnconfigure(0, weight=1)
    optional_frame.columnconfigure(1, weight=1)
    
    ttk.Label(optional_frame, text="Optional Formats:", style='Heading.TLabel').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
    
    # Initialize variables if they don't exist
    if not hasattr(gui_instance, 'export_json_var'):
        gui_instance.export_json_var = tk.BooleanVar(value=False)
    if not hasattr(gui_instance, 'export_excel_var'):
        gui_instance.export_excel_var = tk.BooleanVar(value=False)
    
    # JSON export
    json_check = ttk.Checkbutton(optional_frame, text="📋 JSON (structured data)",
                               variable=gui_instance.export_json_var)
    json_check.grid(row=1, column=0, sticky=tk.W, pady=2)
    
    # Excel export
    excel_check = ttk.Checkbutton(optional_frame, text="📊 Excel (multi-sheet with summary)",
                                variable=gui_instance.export_excel_var)
    excel_check.grid(row=1, column=1, sticky=tk.W, pady=2)
    
    return current_row + 1

def create_timing_settings_section(parent, gui_instance, current_row):
    """Create timing settings section"""
    
    timing_section = ttk.LabelFrame(parent, text="⏱️ Timing & Performance", 
                                  padding="20", style='Modern.TLabelframe')
    timing_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
    timing_section.columnconfigure(1, weight=1)
    
    # Initialize variables if they don't exist
    if not hasattr(gui_instance, 'delay_var'):
        gui_instance.delay_var = tk.StringVar(value="3")
    if not hasattr(gui_instance, 'retry_var'):
        gui_instance.retry_var = tk.StringVar(value="3")
    
    # Page delay
    ttk.Label(timing_section, text="Page Delay (seconds):", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
    delay_spin = ttk.Spinbox(timing_section, from_=1, to=10, textvariable=gui_instance.delay_var, width=10)
    delay_spin.grid(row=0, column=1, sticky=tk.W, pady=(0, 10), padx=(10, 0))
    
    # Max retries
    ttk.Label(timing_section, text="Max Retries:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
    retry_spin = ttk.Spinbox(timing_section, from_=1, to=10, textvariable=gui_instance.retry_var, width=10)
    retry_spin.grid(row=1, column=1, sticky=tk.W, pady=(0, 10), padx=(10, 0))
    
    return current_row + 1

def create_performance_section(parent, gui_instance, current_row):
    """Create performance section"""
    
    performance_section = ttk.LabelFrame(parent, text="🚀 Performance", 
                                       padding="20", style='Modern.TLabelframe')
    performance_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
    performance_section.columnconfigure(1, weight=1)
    
    # Initialize variables if they don't exist
    if not hasattr(gui_instance, 'concurrent_var'):
        gui_instance.concurrent_var = tk.BooleanVar(value=True)
    if not hasattr(gui_instance, 'workers_var'):
        gui_instance.workers_var = tk.StringVar(value="4")
    
    # Concurrent processing
    concurrent_check = ttk.Checkbutton(performance_section, text="⚡ Enable concurrent processing (faster scraping)",
                                     variable=gui_instance.concurrent_var)
    concurrent_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
    
    # Concurrent workers
    ttk.Label(performance_section, text="Concurrent workers:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
    workers_spin = ttk.Spinbox(performance_section, from_=1, to=8, textvariable=gui_instance.workers_var, width=10)
    workers_spin.grid(row=1, column=1, sticky=tk.W, pady=(0, 10), padx=(10, 0))
    
    # Recommendation
    ttk.Label(performance_section, text="💡 Recommended: 2-6 workers (more may trigger bot detection)",
             style='Info.TLabel', wraplength=400).grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
    
    return current_row + 1

def create_action_buttons_section(parent, gui_instance, current_row):
    """Create action buttons section"""
    
    action_section = ttk.LabelFrame(parent, text="🎯 Actions", 
                                  padding="20", style='Modern.TLabelframe')
    action_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
    action_section.columnconfigure(0, weight=1)
    
    # Buttons frame
    buttons_frame = ttk.Frame(action_section)
    buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
    buttons_frame.columnconfigure(0, weight=1)
    buttons_frame.columnconfigure(1, weight=1)
    
    # Start scraping button
    start_btn = ttk.Button(buttons_frame, text="🚀 Start Scraping",
                         command=lambda: print("Start scraping"), style='Primary.TButton')
    start_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10), pady=5)
    
    # Stop scraping button
    stop_btn = ttk.Button(buttons_frame, text="⏹️ Stop Scraping",
                        command=lambda: print("Stop scraping"), style='Secondary.TButton')
    stop_btn.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
    
    return current_row + 1

if __name__ == "__main__":
    # Test the scrollable frame
    root = tk.Tk()
    root.title("Scrollable Frame Test")
    root.geometry("800x600")
    
    # Create a mock GUI instance for testing
    class MockGUI:
        pass
    
    mock_gui = MockGUI()
    
    # Create the enhanced scrollable control panel
    scrollable_panel = create_enhanced_scrollable_control_panel(root, mock_gui)
    scrollable_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    root.mainloop()
