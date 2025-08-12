#!/usr/bin/env python3
"""
Configuration Panel - User-friendly settings interface
Handles all scraping configuration options
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable


class ConfigurationPanel:
    """
    User-friendly configuration panel for scraping settings
    Designed for non-technical users
    """
    
    def __init__(self, parent, style_manager, config_callback: Callable = None):
        """
        Initialize configuration panel
        
        Args:
            parent: Parent widget
            style_manager: StyleManager instance
            config_callback: Callback when configuration changes
        """
        
        self.parent = parent
        self.style_manager = style_manager
        self.config_callback = config_callback
        
        # Configuration variables
        self.config_vars = {
            'city': tk.StringVar(value='gurgaon'),
            'max_pages': tk.StringVar(value='100'),
            'individual_pages': tk.BooleanVar(value=False),
            'force_rescrape': tk.BooleanVar(value=False),
            'export_csv': tk.BooleanVar(value=True),
            'export_json': tk.BooleanVar(value=False),
            'export_excel': tk.BooleanVar(value=False),
            'export_database': tk.BooleanVar(value=True),
            'concurrent_enabled': tk.BooleanVar(value=True),
            'concurrent_workers': tk.StringVar(value='4'),
            'delay_min': tk.StringVar(value='2'),
            'delay_max': tk.StringVar(value='6')
        }
        
        # Bind change events
        for var in self.config_vars.values():
            if isinstance(var, tk.StringVar):
                var.trace('w', self._on_config_change)
            else:
                var.trace('w', self._on_config_change)
        
        # Create the panel
        self.create_panel()

        # Store reference to action buttons for external control
        self.start_button = None
        self.stop_button = None
    
    def create_panel(self):
        """Create the configuration panel"""
        
        # Main container
        self.frame = ttk.Frame(self.parent, style='Card.TFrame', width=380)
        self.frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        self.frame.pack_propagate(False)
        
        # Scrollable content
        self.create_scrollable_content()
        
        # Configuration sections
        self.create_basic_settings()
        self.create_advanced_settings()
        self.create_export_settings()
        self.create_performance_settings()
        self.create_action_buttons()
    
    def create_scrollable_content(self):
        """Create scrollable content area"""
        
        # Canvas for scrolling
        self.canvas = tk.Canvas(self.frame, 
                               bg=self.style_manager.get_color('bg_card'),
                               highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content frame
        self.content_frame = tk.Frame(self.canvas, bg=self.style_manager.get_color('bg_card'))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor=tk.NW)
        
        # Bind events
        self.content_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
    
    def create_basic_settings(self):
        """Create basic settings section"""
        
        # Section header
        header_frame = tk.Frame(self.content_frame, bg=self.style_manager.get_color('bg_card'))
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="🏙️ Basic Settings", style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Essential configuration for scraping", style='Small.TLabel').pack(anchor=tk.W)
        
        # City selection
        city_frame = self._create_setting_frame("📍 City")
        ttk.Label(city_frame, text="Select the city to scrape properties from:", style='Body.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        city_combo = ttk.Combobox(city_frame, 
                                 textvariable=self.config_vars['city'],
                                 values=['gurgaon', 'mumbai', 'delhi', 'bangalore', 'pune', 'hyderabad', 'chennai', 'kolkata'],
                                 state='readonly',
                                 style='Modern.TCombobox',
                                 font=self.style_manager.get_font('body'))
        city_combo.pack(fill=tk.X, pady=(0, 5))
        
        # Help text
        ttk.Label(city_frame, text="💡 Tip: Start with smaller cities for faster results", style='Small.TLabel').pack(anchor=tk.W)
        
        # Pages setting
        pages_frame = self._create_setting_frame("📄 Number of Pages")
        ttk.Label(pages_frame, text="How many pages to scrape (each page ≈ 30 properties):", style='Body.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        pages_entry = tk.Entry(pages_frame,
                              textvariable=self.config_vars['max_pages'],
                              font=self.style_manager.get_font('body'),
                              relief='flat',
                              bd=5,
                              bg=self.style_manager.get_color('bg_main'))
        pages_entry.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(pages_frame, text="💡 Recommended: 50-200 pages for comprehensive data", style='Small.TLabel').pack(anchor=tk.W)
        
        # Individual pages option
        individual_frame = self._create_setting_frame("🏠 Detailed Property Data")
        
        individual_check = tk.Checkbutton(individual_frame,
                                        text="Extract detailed information from individual property pages",
                                        variable=self.config_vars['individual_pages'],
                                        bg=self.style_manager.get_color('bg_card'),
                                        fg=self.style_manager.get_color('text_primary'),
                                        font=self.style_manager.get_font('body'),
                                        activebackground=self.style_manager.get_color('bg_card'),
                                        wraplength=320)
        individual_check.pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(individual_frame, text="⚠️ Note: This will significantly increase scraping time", style='Warning.TLabel').pack(anchor=tk.W)
        
        # Force rescrape option
        force_check = tk.Checkbutton(individual_frame,
                                   text="Force re-scrape individual properties (ignore duplicates)",
                                   variable=self.config_vars['force_rescrape'],
                                   bg=self.style_manager.get_color('bg_card'),
                                   fg=self.style_manager.get_color('text_secondary'),
                                   font=self.style_manager.get_font('small'),
                                   activebackground=self.style_manager.get_color('bg_card'),
                                   wraplength=320)
        force_check.pack(anchor=tk.W, pady=(5, 0))
    
    def create_advanced_settings(self):
        """Create advanced settings section"""
        
        # Section header
        header_frame = tk.Frame(self.content_frame, bg=self.style_manager.get_color('bg_card'))
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="⚙️ Advanced Settings", style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Fine-tune scraping behavior", style='Small.TLabel').pack(anchor=tk.W)
        
        # Concurrent processing
        concurrent_frame = self._create_setting_frame("⚡ Performance")
        
        concurrent_check = tk.Checkbutton(concurrent_frame,
                                        text="Enable concurrent processing (faster scraping)",
                                        variable=self.config_vars['concurrent_enabled'],
                                        bg=self.style_manager.get_color('bg_card'),
                                        fg=self.style_manager.get_color('text_primary'),
                                        font=self.style_manager.get_font('body'),
                                        activebackground=self.style_manager.get_color('bg_card'),
                                        wraplength=320)
        concurrent_check.pack(anchor=tk.W, pady=(0, 10))
        
        # Workers setting
        workers_subframe = tk.Frame(concurrent_frame, bg=self.style_manager.get_color('bg_card'))
        workers_subframe.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(workers_subframe, text="Concurrent workers:", style='Body.TLabel').pack(side=tk.LEFT)
        workers_entry = tk.Entry(workers_subframe,
                               textvariable=self.config_vars['concurrent_workers'],
                               font=self.style_manager.get_font('body'),
                               width=5,
                               relief='flat',
                               bd=3,
                               bg=self.style_manager.get_color('bg_main'))
        workers_entry.pack(side=tk.RIGHT)
        
        ttk.Label(concurrent_frame, text="💡 Recommended: 2-6 workers (more may trigger bot detection)", style='Small.TLabel').pack(anchor=tk.W)
    
    def create_export_settings(self):
        """Create export settings section"""
        
        # Section header
        header_frame = tk.Frame(self.content_frame, bg=self.style_manager.get_color('bg_card'))
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="💾 Export Options", style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Choose how to save your data", style='Small.TLabel').pack(anchor=tk.W)
        
        export_frame = self._create_setting_frame("📁 File Formats")
        
        # Export checkboxes
        export_options = [
            ('export_csv', 'CSV (Excel compatible)', True),
            ('export_database', 'Database (SQLite)', True),
            ('export_json', 'JSON (for developers)', False),
            ('export_excel', 'Excel (.xlsx)', False)
        ]
        
        for var_name, label, recommended in export_options:
            check_frame = tk.Frame(export_frame, bg=self.style_manager.get_color('bg_card'))
            check_frame.pack(fill=tk.X, pady=2)
            
            checkbox = tk.Checkbutton(check_frame,
                                    text=label,
                                    variable=self.config_vars[var_name],
                                    bg=self.style_manager.get_color('bg_card'),
                                    fg=self.style_manager.get_color('text_primary'),
                                    font=self.style_manager.get_font('body'),
                                    activebackground=self.style_manager.get_color('bg_card'))
            checkbox.pack(side=tk.LEFT)
            
            if recommended:
                ttk.Label(check_frame, text="✅", style='Success.TLabel').pack(side=tk.RIGHT)
    
    def create_performance_settings(self):
        """Create performance settings section"""
        
        # Section header
        header_frame = tk.Frame(self.content_frame, bg=self.style_manager.get_color('bg_card'))
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        ttk.Label(header_frame, text="🛡️ Anti-Detection", style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(header_frame, text="Prevent blocking and ensure reliability", style='Small.TLabel').pack(anchor=tk.W)
        
        delay_frame = self._create_setting_frame("⏱️ Request Delays")
        
        # Delay settings
        delay_subframe = tk.Frame(delay_frame, bg=self.style_manager.get_color('bg_card'))
        delay_subframe.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(delay_subframe, text="Min delay (seconds):", style='Body.TLabel').pack(side=tk.LEFT)
        min_entry = tk.Entry(delay_subframe,
                           textvariable=self.config_vars['delay_min'],
                           font=self.style_manager.get_font('body'),
                           width=5,
                           relief='flat',
                           bd=3,
                           bg=self.style_manager.get_color('bg_main'))
        min_entry.pack(side=tk.RIGHT)
        
        delay_subframe2 = tk.Frame(delay_frame, bg=self.style_manager.get_color('bg_card'))
        delay_subframe2.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(delay_subframe2, text="Max delay (seconds):", style='Body.TLabel').pack(side=tk.LEFT)
        max_entry = tk.Entry(delay_subframe2,
                           textvariable=self.config_vars['delay_max'],
                           font=self.style_manager.get_font('body'),
                           width=5,
                           relief='flat',
                           bd=3,
                           bg=self.style_manager.get_color('bg_main'))
        max_entry.pack(side=tk.RIGHT)
        
        ttk.Label(delay_frame, text="💡 Longer delays = more reliable but slower", style='Small.TLabel').pack(anchor=tk.W)
    
    def create_action_buttons(self):
        """Create action buttons"""
        
        buttons_frame = tk.Frame(self.content_frame, bg=self.style_manager.get_color('bg_card'))
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Start button
        self.start_button = ttk.Button(buttons_frame,
                                     text="🚀 Start Scraping",
                                     style='Primary.TButton',
                                     command=self._start_scraping)
        self.start_button.pack(fill=tk.X, pady=(0, 10))

        # Stop button
        self.stop_button = ttk.Button(buttons_frame,
                                    text="⏹️ Stop Scraping",
                                    style='Warning.TButton',
                                    command=self._stop_scraping,
                                    state='disabled')
        self.stop_button.pack(fill=tk.X, pady=(0, 10))
        
        # Quick settings buttons
        quick_frame = tk.Frame(buttons_frame, bg=self.style_manager.get_color('bg_card'))
        quick_frame.pack(fill=tk.X)
        
        ttk.Button(quick_frame,
                  text="⚡ Quick Setup",
                  style='Secondary.TButton',
                  command=self._quick_setup).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(quick_frame,
                  text="🔄 Reset",
                  style='Secondary.TButton',
                  command=self._reset_config).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
    
    def _create_setting_frame(self, title: str) -> tk.Frame:
        """Create a setting frame with title"""
        
        container = tk.Frame(self.content_frame, bg=self.style_manager.get_color('bg_card'))
        container.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        ttk.Label(container, text=title, style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 8))
        
        return container
    
    def _on_frame_configure(self, event):
        """Handle frame configuration changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Handle canvas configuration changes"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _on_config_change(self, *args):
        """Handle configuration changes"""
        if self.config_callback:
            self.config_callback(self.get_config())
    
    def _start_scraping(self):
        """Start scraping with current configuration"""
        if self.config_callback:
            self.config_callback(self.get_config(), action='start')

    def _stop_scraping(self):
        """Stop scraping"""
        if self.config_callback:
            self.config_callback(self.get_config(), action='stop')
    
    def _quick_setup(self):
        """Apply quick setup configuration"""
        self.config_vars['max_pages'].set('50')
        self.config_vars['individual_pages'].set(False)
        self.config_vars['concurrent_enabled'].set(True)
        self.config_vars['concurrent_workers'].set('4')
        self.config_vars['export_csv'].set(True)
        self.config_vars['export_database'].set(True)
    
    def _reset_config(self):
        """Reset configuration to defaults"""
        self.config_vars['city'].set('gurgaon')
        self.config_vars['max_pages'].set('100')
        self.config_vars['individual_pages'].set(False)
        self.config_vars['force_rescrape'].set(False)
        self.config_vars['export_csv'].set(True)
        self.config_vars['export_json'].set(False)
        self.config_vars['export_excel'].set(False)
        self.config_vars['export_database'].set(True)
        self.config_vars['concurrent_enabled'].set(True)
        self.config_vars['concurrent_workers'].set('4')
        self.config_vars['delay_min'].set('2')
        self.config_vars['delay_max'].set('6')
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        
        config = {}
        for key, var in self.config_vars.items():
            if isinstance(var, tk.BooleanVar):
                config[key] = var.get()
            else:
                value = var.get()
                # Convert numeric strings to integers
                if key in ['max_pages', 'concurrent_workers', 'delay_min', 'delay_max']:
                    try:
                        config[key] = int(float(value))
                    except ValueError:
                        config[key] = 0
                else:
                    config[key] = value
        
        return config
    
    def set_config(self, config: Dict[str, Any]):
        """Set configuration values"""
        
        for key, value in config.items():
            if key in self.config_vars:
                self.config_vars[key].set(value)
