#!/usr/bin/env python3
"""
MagicBricks Scraper GUI Application
Modern, professional interface for property data extraction with advanced features.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import our integrated scraper and multi-city system
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode
from multi_city_system import MultiCitySystem, CityTier, Region
from error_handling_system import ErrorHandlingSystem, ErrorSeverity, ErrorCategory


class MagicBricksGUI:
    """
    Modern, professional GUI application for MagicBricks scraper with advanced features
    """

    def __init__(self):
        """Initialize the GUI application"""

        # Create main window with enhanced configuration
        self.root = tk.Tk()
        self.root.title("🏠 MagicBricks Property Scraper - Professional Edition v2.0")
        self.root.geometry("1450x950")
        self.root.minsize(1250, 850)
        
        # Enhanced window styling and effects
        self.root.configure(bg='#f8fafc')
        
        # Add modern window effects (platform-specific)
        try:
            # Subtle transparency for modern look
            self.root.wm_attributes('-alpha', 0.98)
            # Remove window decorations for custom styling (optional)
            # self.root.overrideredirect(False)
        except:
            pass  # Not supported on all platforms
        
        # Try to set window icon (if available)
        try:
            # You can add an icon file here if you have one
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass

        # Configure modern styling
        self.setup_modern_styles()

        # Initialize variables
        self.scraper = None
        self.scraping_thread = None
        self.is_scraping = False
        self.message_queue = queue.Queue()

        # Progress tracking
        self.scraping_start_time = None
        self.last_update_time = None
        self.progress_history = []

        # Multi-city system
        self.city_system = MultiCitySystem()
        self.selected_cities = ['gurgaon']  # Default selection

        # Error handling system
        self.error_system = ErrorHandlingSystem()
        self.error_system.register_callback(self.on_error_callback)

        # Configuration with better defaults
        self.config = {
            'city': 'gurgaon',
            'mode': ScrapingMode.INCREMENTAL,
            'max_pages': 100,
            'headless': True,
            'output_directory': str(Path.cwd()),
            'incremental_enabled': True,
            'page_delay': 3,
            'max_retries': 2,
            'export_json': False,
            'export_excel': False,
            'individual_pages': False
        }

        # Create modern GUI components
        self.create_modern_interface()

        # Initialize selected cities display
        self.update_selected_cities_display()

        # Start message processing
        self.process_messages()

        print("🎮 MagicBricks GUI v2.0 Initialized")
        print(f"   🏙️ Multi-city system: {len(self.city_system.cities)} cities available")
        print(f"   🎨 Modern interface with scrollable panels")
    
    def setup_modern_styles(self):
        """Setup modern, professional styling for the GUI with enhanced visual appeal"""

        # Configure ttk styles
        self.style = ttk.Style()

        # Use modern theme
        try:
            self.style.theme_use('clam')
        except:
            self.style.theme_use('default')

        # Enhanced modern color palette with gradients and depth
        self.colors = {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8fafc',
            'bg_accent': '#e2e8f0',
            'bg_dark': '#1e293b',
            'bg_card': '#ffffff',
            'primary': '#3b82f6',
            'primary_dark': '#1d4ed8',
            'primary_light': '#93c5fd',
            'success': '#10b981',
            'success_light': '#6ee7b7',
            'warning': '#f59e0b',
            'warning_light': '#fbbf24',
            'danger': '#ef4444',
            'danger_light': '#f87171',
            'info': '#06b6d4',
            'info_light': '#67e8f9',
            'dark': '#0f172a',
            'light': '#f8fafc',
            'border': '#e2e8f0',
            'border_light': '#f1f5f9',
            'text_primary': '#0f172a',
            'text_secondary': '#64748b',
            'text_muted': '#94a3b8',
            'shadow': '#00000010',
            'gradient_start': '#3b82f6',
            'gradient_end': '#1d4ed8'
        }

        # Configure enhanced modern styles with better typography
        self.style.configure('Title.TLabel',
                           font=('Segoe UI', 20, 'bold'),
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'])

        self.style.configure('Subtitle.TLabel',
                           font=('Segoe UI', 12),
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_secondary'])

        self.style.configure('Heading.TLabel',
                           font=('Segoe UI', 11, 'bold'),
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'])

        self.style.configure('Info.TLabel',
                           font=('Segoe UI', 10),
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_secondary'])

        self.style.configure('Success.TLabel',
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['bg_primary'],
                           foreground=self.colors['success'])

        self.style.configure('Warning.TLabel',
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['bg_primary'],
                           foreground=self.colors['warning'])

        self.style.configure('Error.TLabel',
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['bg_primary'],
                           foreground=self.colors['danger'])

        self.style.configure('Muted.TLabel',
                           font=('Segoe UI', 9),
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_muted'])

        # Enhanced modern button styles with better visual hierarchy
        self.style.configure('Primary.TButton',
                           font=('Segoe UI', 11, 'bold'),
                           padding=(25, 12),
                           relief='flat')
        
        self.style.map('Primary.TButton',
                      background=[('active', self.colors['primary_dark']),
                                ('!active', self.colors['primary'])],
                      foreground=[('active', 'white'),
                                ('!active', 'white')])

        self.style.configure('Success.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(20, 10),
                           relief='flat')
        
        self.style.map('Success.TButton',
                      background=[('active', '#059669'),
                                ('!active', self.colors['success'])],
                      foreground=[('active', 'white'),
                                ('!active', 'white')])

        self.style.configure('Secondary.TButton',
                           font=('Segoe UI', 10),
                           padding=(15, 8),
                           relief='flat')
        
        self.style.map('Secondary.TButton',
                      background=[('active', self.colors['bg_accent']),
                                ('!active', self.colors['bg_secondary'])],
                      foreground=[('active', self.colors['text_primary']),
                                ('!active', self.colors['text_secondary'])])

        self.style.configure('Danger.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           padding=(15, 8),
                           relief='flat')
        
        self.style.map('Danger.TButton',
                      background=[('active', '#dc2626'),
                                ('!active', self.colors['danger'])],
                      foreground=[('active', 'white'),
                                ('!active', 'white')])

        # Enhanced frame styles with modern cards
        self.style.configure('Card.TFrame',
                           background=self.colors['bg_card'],
                           relief='flat',
                           borderwidth=0)

        self.style.configure('Sidebar.TFrame',
                           background=self.colors['bg_secondary'],
                           relief='flat')
        
        self.style.configure('Modern.TLabelframe',
                           background=self.colors['bg_card'],
                           relief='flat',
                           borderwidth=1,
                           lightcolor=self.colors['border'],
                           darkcolor=self.colors['border'])
        
        self.style.configure('Modern.TLabelframe.Label',
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'],
                           font=('Segoe UI', 11, 'bold'))

        # Enhanced entry and combobox styles
        self.style.configure('Modern.TEntry',
                           fieldbackground=self.colors['bg_primary'],
                           borderwidth=2,
                           relief='flat',
                           insertcolor=self.colors['primary'])
        
        self.style.map('Modern.TEntry',
                      focuscolor=[('focus', self.colors['primary'])],
                      bordercolor=[('focus', self.colors['primary']),
                                 ('!focus', self.colors['border'])])

        self.style.configure('Modern.TCombobox',
                           fieldbackground=self.colors['bg_primary'],
                           borderwidth=2,
                           relief='flat')
        
        self.style.map('Modern.TCombobox',
                      focuscolor=[('focus', self.colors['primary'])],
                      bordercolor=[('focus', self.colors['primary']),
                                 ('!focus', self.colors['border'])])

        # Progress bar styling
        self.style.configure('Modern.Horizontal.TProgressbar',
                           background=self.colors['primary'],
                           troughcolor=self.colors['bg_accent'],
                           borderwidth=0,
                           lightcolor=self.colors['primary'],
                           darkcolor=self.colors['primary'])
    
    def create_modern_interface(self):
        """Create modern, professional interface with proper scrolling"""

        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Configure grid weights
        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=2)
        main_container.rowconfigure(1, weight=1)

        # Header section
        self.create_header(main_container)

        # Main content area with two panels
        content_frame = ttk.Frame(main_container)
        content_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)

        # Left panel (controls) - with scrolling
        self.create_scrollable_control_panel(content_frame)

        # Right panel (monitoring and logs)
        self.create_monitoring_panel(content_frame)

        # Bottom status bar
        self.create_modern_status_bar(main_container)

    def create_header(self, parent):
        """Create modern header section with enhanced visual appeal"""

        # Main header container with gradient-like effect
        header_container = ttk.Frame(parent)
        header_container.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        header_container.columnconfigure(0, weight=1)

        # Primary header card
        header_frame = ttk.Frame(header_container, style='Card.TFrame')
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        header_frame.columnconfigure(1, weight=1)

        # Left side - Icon and title with better spacing
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, sticky=tk.W, padx=25, pady=20)

        # Enhanced icon with background
        icon_frame = ttk.Frame(title_frame)
        icon_frame.pack(side=tk.LEFT)
        
        icon_label = ttk.Label(icon_frame, text="🏠", font=('Segoe UI', 28))
        icon_label.pack()

        # Title section with better typography
        title_text_frame = ttk.Frame(title_frame)
        title_text_frame.pack(side=tk.LEFT, padx=(15, 0))

        # Main title with enhanced styling
        main_title = ttk.Label(title_text_frame, text="MagicBricks Property Scraper",
                              style='Title.TLabel')
        main_title.pack(anchor=tk.W)
        
        # Subtitle with better description
        subtitle = ttk.Label(title_text_frame, 
                            text="Professional Edition v2.0 • Advanced Property Data Extraction",
                            style='Subtitle.TLabel')
        subtitle.pack(anchor=tk.W, pady=(2, 0))
        
        # Feature highlights
        features = ttk.Label(title_text_frame, 
                            text="⚡ Incremental Scraping • 🏙️ Multi-City Support • 📊 Advanced Analytics",
                            style='Muted.TLabel')
        features.pack(anchor=tk.W, pady=(5, 0))

        # Right side - Enhanced stats and status
        stats_frame = ttk.Frame(header_frame)
        stats_frame.grid(row=0, column=1, sticky=tk.E, padx=25, pady=20)

        # Status indicators
        status_frame = ttk.Frame(stats_frame)
        status_frame.pack(anchor=tk.E)
        
        # System status
        system_status = ttk.Label(status_frame, text="🟢 System Ready", 
                                 style='Success.TLabel', font=('Segoe UI', 10, 'bold'))
        system_status.pack(anchor=tk.E)
        
        # Version badge
        version_badge = ttk.Label(status_frame, text="v2.0.0 • Build 2024",
                                 style='Info.TLabel')
        version_badge.pack(anchor=tk.E, pady=(3, 0))
        
        # Quick stats
        stats_text = ttk.Label(status_frame, text="Ready for Multi-City Scraping",
                              style='Muted.TLabel')
        stats_text.pack(anchor=tk.E, pady=(2, 0))
    
    def create_scrollable_control_panel(self, parent):
        """Create enhanced scrollable control panel with reliable scrolling"""

        # Control panel container with modern styling
        control_container = ttk.LabelFrame(parent, text="📋 Scraping Configuration",
                                         padding="15", style='Modern.TLabelframe')
        control_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        control_container.columnconfigure(0, weight=1)
        control_container.rowconfigure(0, weight=1)

        # Create enhanced scrollable frame using reliable implementation
        self.scrollable_panel = self.create_enhanced_scrollable_frame(control_container)
        self.scrollable_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Get the frame to add controls to
        scrollable_frame = self.scrollable_panel.get_frame()
        scrollable_frame.columnconfigure(0, weight=1)

        # Now create all the controls in the scrollable frame
        self.create_control_sections(scrollable_frame)

    def create_enhanced_scrollable_frame(self, container):
        """Create a reliable scrollable frame implementation"""

        class EnhancedScrollableFrame(ttk.Frame):
            def __init__(self, parent, *args, **kwargs):
                super().__init__(parent, *args, **kwargs)

                # Create canvas and scrollbar
                try:
                    bg_color = self.master.master.colors['bg_primary']
                except (AttributeError, KeyError):
                    bg_color = '#f8fafc'  # Default background color
                self.canvas = tk.Canvas(self, highlightthickness=0, bg=bg_color)
                self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
                self.scrollable_frame = ttk.Frame(self.canvas)

                # Configure scrolling with improved handling
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

                # Bind enhanced mouse wheel events
                self.bind_enhanced_mousewheel()

                # Bind canvas resize for responsive width
                self.canvas.bind('<Configure>', self.on_canvas_configure)

                # Force initial update
                self.after(100, self.update_scroll_region)

            def bind_enhanced_mousewheel(self):
                """Enhanced mouse wheel binding that works reliably"""

                def _on_mousewheel(event):
                    # Improved scrolling with better sensitivity
                    self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

                def _bind_to_mousewheel(event):
                    self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

                def _unbind_from_mousewheel(event):
                    self.canvas.unbind_all("<MouseWheel>")

                # Bind when mouse enters the frame
                self.bind('<Enter>', _bind_to_mousewheel)
                self.bind('<Leave>', _unbind_from_mousewheel)

                # Also bind to canvas and scrollable frame
                self.canvas.bind('<Enter>', _bind_to_mousewheel)
                self.canvas.bind('<Leave>', _unbind_from_mousewheel)
                self.scrollable_frame.bind('<Enter>', _bind_to_mousewheel)
                self.scrollable_frame.bind('<Leave>', _unbind_from_mousewheel)

            def on_canvas_configure(self, event):
                """Handle canvas resize to adjust scrollable frame width"""
                canvas_width = event.width
                self.canvas.itemconfig(self.canvas_window, width=canvas_width)

            def update_scroll_region(self):
                """Force update of scroll region"""
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            def get_frame(self):
                """Get the scrollable frame to add widgets to"""
                return self.scrollable_frame

        return EnhancedScrollableFrame(container)

    def create_control_sections(self, parent):
        """Create all control sections in the scrollable frame with enhanced visibility"""

        parent.columnconfigure(0, weight=1)
        current_row = 0

        # Add top padding for better spacing
        ttk.Frame(parent, height=10).grid(row=current_row, column=0)
        current_row += 1

        # === CITY SELECTION SECTION ===
        city_section = ttk.LabelFrame(parent, text="🏙️ City Selection",
                                    padding="20", style='Modern.TLabelframe')
        city_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        city_section.columnconfigure(1, weight=1)
        current_row += 1

        ttk.Label(city_section, text="Selected Cities:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Selected cities display with better styling
        if not hasattr(self, 'selected_cities_var'):
            self.selected_cities_var = tk.StringVar(value="Gurgaon")
        cities_frame = ttk.Frame(city_section)
        cities_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        cities_frame.columnconfigure(0, weight=1)

        selected_cities_label = ttk.Label(cities_frame, textvariable=self.selected_cities_var,
                                        style='Info.TLabel', relief='solid', padding="12")
        selected_cities_label.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))

        select_cities_btn = ttk.Button(cities_frame, text="🌍 Select Cities",
                                     command=self.open_city_selector, style='Secondary.TButton')
        select_cities_btn.grid(row=0, column=1)

        # === SCRAPING MODE SECTION ===
        mode_section = ttk.LabelFrame(parent, text="⚙️ Scraping Mode", 
                                    padding="20", style='Modern.TLabelframe')
        mode_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        mode_section.columnconfigure(1, weight=1)
        current_row += 1

        ttk.Label(mode_section, text="Mode:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.mode_var = tk.StringVar(value=self.config['mode'].value)
        mode_combo = ttk.Combobox(mode_section, textvariable=self.mode_var, width=25, 
                                state='readonly', style='Modern.TCombobox')
        mode_combo['values'] = ('incremental', 'full', 'conservative', 'date_range', 'custom')
        mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 15), padx=(15, 0))
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_changed)

        # Mode description with better formatting
        self.mode_desc_var = tk.StringVar()
        self.update_mode_description()
        mode_desc_label = ttk.Label(mode_section, textvariable=self.mode_desc_var,
                                   style='Info.TLabel', wraplength=400)
        mode_desc_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # === BASIC SETTINGS SECTION ===
        basic_section = ttk.LabelFrame(parent, text="📊 Basic Settings", 
                                     padding="20", style='Modern.TLabelframe')
        basic_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        basic_section.columnconfigure(1, weight=1)
        current_row += 1

        # Max pages with icon
        ttk.Label(basic_section, text="📄 Max Pages:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        self.max_pages_var = tk.StringVar(value=str(self.config['max_pages']))
        max_pages_entry = ttk.Entry(basic_section, textvariable=self.max_pages_var, 
                                  width=15, style='Modern.TEntry')
        max_pages_entry.grid(row=0, column=1, sticky=tk.W, pady=(0, 15), padx=(15, 0))

        # Output directory with icon
        ttk.Label(basic_section, text="📁 Output Directory:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 8))
        output_frame = ttk.Frame(basic_section)
        output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 15), padx=(15, 0))
        output_frame.columnconfigure(0, weight=1)

        self.output_dir_var = tk.StringVar(value=self.config['output_directory'])
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, style='Modern.TEntry')
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))

        browse_btn = ttk.Button(output_frame, text="📂 Browse", command=self.browse_output_directory,
                              style='Secondary.TButton')
        browse_btn.grid(row=0, column=1)

        # === ADVANCED OPTIONS SECTION ===
        advanced_section = ttk.LabelFrame(parent, text="[SETUP] Advanced Options", 
                                        padding="20", style='Modern.TLabelframe')
        advanced_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        advanced_section.columnconfigure(0, weight=1)
        current_row += 1

        # Checkboxes in a grid layout
        checkbox_frame = ttk.Frame(advanced_section)
        checkbox_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        checkbox_frame.columnconfigure(0, weight=1)
        checkbox_frame.columnconfigure(1, weight=1)

        # Headless mode
        self.headless_var = tk.BooleanVar(value=self.config['headless'])
        headless_check = ttk.Checkbutton(checkbox_frame, text="[ROCKET] Headless Mode (faster)",
                                       variable=self.headless_var)
        headless_check.grid(row=0, column=0, sticky=tk.W, pady=2)

        # Incremental enabled
        self.incremental_var = tk.BooleanVar(value=self.config['incremental_enabled'])
        incremental_check = ttk.Checkbutton(checkbox_frame, text="⚡ Incremental Scraping (60-75% faster)",
                                          variable=self.incremental_var)
        incremental_check.grid(row=0, column=1, sticky=tk.W, pady=2)

        # Individual property pages
        self.individual_pages_var = tk.BooleanVar(value=self.config['individual_pages'])
        individual_check = ttk.Checkbutton(checkbox_frame, text="📄 Individual Property Details (⚠️ 10x slower)",
                                         variable=self.individual_pages_var,
                                         command=self.on_individual_pages_changed)
        individual_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)

        # Individual pages warning
        self.individual_info_var = tk.StringVar()
        self.update_individual_pages_info()
        individual_info_label = ttk.Label(advanced_section, textvariable=self.individual_info_var,
                                        style='Warning.TLabel', wraplength=400)
        individual_info_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        # === INDIVIDUAL PROPERTY MANAGEMENT SECTION ===
        individual_mgmt_section = ttk.LabelFrame(parent, text="🏠 Individual Property Management",
                                               padding="20", style='Modern.TLabelframe')
        individual_mgmt_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        individual_mgmt_section.columnconfigure(1, weight=1)
        current_row += 1

        # Scraping mode selection for individual properties
        ttk.Label(individual_mgmt_section, text="Individual Scraping Mode:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.individual_mode_var = tk.StringVar(value="with_listing")
        individual_mode_combo = ttk.Combobox(individual_mgmt_section, textvariable=self.individual_mode_var,
                                           state='readonly', style='Modern.TCombobox')
        individual_mode_combo['values'] = ('with_listing', 'individual_only', 'skip_individual')
        individual_mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(15, 0))
        individual_mode_combo.bind('<<ComboboxSelected>>', self.on_individual_mode_changed)

        # Mode description
        self.individual_mode_desc_var = tk.StringVar()
        self.update_individual_mode_description()
        individual_mode_desc_label = ttk.Label(individual_mgmt_section, textvariable=self.individual_mode_desc_var,
                                             style='Info.TLabel', wraplength=400)
        individual_mode_desc_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Individual property count control
        ttk.Label(individual_mgmt_section, text="Max Individual Properties:", style='Heading.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        individual_count_frame = ttk.Frame(individual_mgmt_section)
        individual_count_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(15, 0))
        individual_count_frame.columnconfigure(0, weight=1)

        self.individual_count_var = tk.StringVar(value="100")
        individual_count_entry = ttk.Entry(individual_count_frame, textvariable=self.individual_count_var, width=10)
        individual_count_entry.grid(row=0, column=0, sticky=tk.W)

        ttk.Label(individual_count_frame, text="(0 = all properties)", style='Muted.TLabel').grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Already scraped properties display
        self.scraped_count_var = tk.StringVar(value="Checking...")
        scraped_info_frame = ttk.Frame(individual_mgmt_section)
        scraped_info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        scraped_info_frame.columnconfigure(1, weight=1)

        ttk.Label(scraped_info_frame, text="Already Scraped:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)
        scraped_count_label = ttk.Label(scraped_info_frame, textvariable=self.scraped_count_var, style='Success.TLabel')
        scraped_count_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        refresh_count_btn = ttk.Button(scraped_info_frame, text="🔄 Refresh",
                                     command=self.refresh_scraped_count, style='Secondary.TButton')
        refresh_count_btn.grid(row=0, column=2, padx=(10, 0))

        # Force re-scrape option
        self.force_rescrape_var = tk.BooleanVar(value=False)
        force_rescrape_check = ttk.Checkbutton(individual_mgmt_section,
                                             text="🔄 Force re-scrape already scraped properties",
                                             variable=self.force_rescrape_var)
        force_rescrape_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        # === EXPORT OPTIONS SECTION ===
        export_section = ttk.LabelFrame(parent, text="[SAVE] Export Options", 
                                      padding="20", style='Modern.TLabelframe')
        export_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        export_section.columnconfigure(0, weight=1)
        current_row += 1

        # Mandatory formats
        ttk.Label(export_section, text="[SUCCESS] Mandatory: CSV + Database",
                 style='Success.TLabel', font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Optional formats
        optional_frame = ttk.Frame(export_section)
        optional_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        optional_frame.columnconfigure(0, weight=1)
        optional_frame.columnconfigure(1, weight=1)

        ttk.Label(optional_frame, text="Optional Formats:", style='Heading.TLabel').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        # JSON export
        self.export_json_var = tk.BooleanVar(value=self.config['export_json'])
        json_check = ttk.Checkbutton(optional_frame, text="📋 JSON (structured data)",
                                   variable=self.export_json_var)
        json_check.grid(row=1, column=0, sticky=tk.W, pady=2)

        # Excel export
        self.export_excel_var = tk.BooleanVar(value=self.config['export_excel'])
        excel_check = ttk.Checkbutton(optional_frame, text="📊 Excel (multi-sheet with summary)",
                                    variable=self.export_excel_var)
        excel_check.grid(row=1, column=1, sticky=tk.W, pady=2)

        # === TIMING SETTINGS SECTION ===
        timing_section = ttk.LabelFrame(parent, text="⏱️ Timing & Performance", padding="15")
        timing_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        timing_section.columnconfigure(1, weight=1)
        current_row += 1

        # Page delay with min/max controls
        ttk.Label(timing_section, text="Page Delay (min-max):", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        page_delay_range_frame = ttk.Frame(timing_section)
        page_delay_range_frame.grid(row=0, column=1, sticky=tk.W, pady=(0, 10), padx=(10, 0))

        # Initialize page delay variables (only once)
        if not hasattr(self, 'page_delay_min_var'):
            self.page_delay_min_var = tk.StringVar(value="2")
        if not hasattr(self, 'page_delay_max_var'):
            self.page_delay_max_var = tk.StringVar(value="2")

        ttk.Spinbox(page_delay_range_frame, from_=1, to=30, textvariable=self.page_delay_min_var, width=5).grid(row=0, column=0)
        ttk.Label(page_delay_range_frame, text=" - ").grid(row=0, column=1)
        ttk.Spinbox(page_delay_range_frame, from_=1, to=30, textvariable=self.page_delay_max_var, width=5).grid(row=0, column=2)
        ttk.Label(page_delay_range_frame, text=" seconds").grid(row=0, column=3)

        # Max retries
        ttk.Label(timing_section, text="Max Retries:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.retry_var = tk.StringVar(value=str(self.config['max_retries']))
        retry_spin = ttk.Spinbox(timing_section, from_=1, to=10, textvariable=self.retry_var, width=10)
        retry_spin.grid(row=1, column=1, sticky=tk.W, pady=(0, 10), padx=(10, 0))

        # Individual page delay range (ALWAYS VISIBLE - not conditional)
        ttk.Label(timing_section, text="Individual Page Delay (min-max):", style='Heading.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(10, 5))

        delay_range_frame = ttk.Frame(timing_section)
        delay_range_frame.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

        # Initialize individual delay variables (only once)
        if not hasattr(self, 'individual_delay_min_var'):
            self.individual_delay_min_var = tk.StringVar(value="1")
        if not hasattr(self, 'individual_delay_max_var'):
            self.individual_delay_max_var = tk.StringVar(value="5")

        ttk.Spinbox(delay_range_frame, from_=1, to=30, textvariable=self.individual_delay_min_var, width=5).grid(row=0, column=0)
        ttk.Label(delay_range_frame, text=" - ").grid(row=0, column=1)
        ttk.Spinbox(delay_range_frame, from_=1, to=30, textvariable=self.individual_delay_max_var, width=5).grid(row=0, column=2)
        ttk.Label(delay_range_frame, text=" seconds").grid(row=0, column=3)

        # Additional timing settings
        ttk.Label(timing_section, text="Batch Break Delay (seconds):", style='Heading.TLabel').grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        if not hasattr(self, 'batch_break_var'):
            self.batch_break_var = tk.StringVar(value="15")
        ttk.Spinbox(timing_section, from_=5, to=60, textvariable=self.batch_break_var, width=10).grid(row=3, column=1, sticky=tk.W, padx=(10, 0))

        # Bot Detection Recovery Delay
        ttk.Label(timing_section, text="Bot Detection Delay (seconds):", style='Heading.TLabel').grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        if not hasattr(self, 'bot_delay_var'):
            self.bot_delay_var = tk.StringVar(value="30")
        ttk.Spinbox(timing_section, from_=10, to=120, textvariable=self.bot_delay_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=(10, 0))

        ttk.Label(timing_section, text="Batch Size:", style='Heading.TLabel').grid(row=4, column=0, sticky=tk.W, pady=(5, 5))
        if not hasattr(self, 'batch_size_var'):
            self.batch_size_var = tk.StringVar(value="10")
        ttk.Spinbox(timing_section, from_=1, to=50, textvariable=self.batch_size_var, width=10).grid(row=4, column=1, sticky=tk.W, padx=(10, 0))

        # Memory optimization
        self.memory_optimization_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(timing_section, text="Memory Optimization", variable=self.memory_optimization_var).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        # Initialize filtering variables with defaults
        self.enable_filtering_var = tk.BooleanVar(value=False)
        self.price_min_var = tk.StringVar(value="")
        self.price_max_var = tk.StringVar(value="")
        self.area_min_var = tk.StringVar(value="")
        self.area_max_var = tk.StringVar(value="")

        # Initially hide individual delay settings
        self.toggle_individual_delay_settings()

        # === PERFORMANCE SETTINGS SECTION ===
        performance_section = ttk.LabelFrame(parent, text="⚡ Performance Settings", padding="15")
        performance_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        performance_section.columnconfigure(1, weight=1)
        current_row += 1

        # Batch size for individual properties
        ttk.Label(performance_section, text="Individual Property Batch Size:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.batch_size_var = tk.StringVar(value="10")
        batch_spinbox = ttk.Spinbox(performance_section, from_=1, to=50, textvariable=self.batch_size_var, width=10)
        batch_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        self.create_tooltip(batch_spinbox, "How many properties to process at once. Higher = faster but uses more memory.")

        # Individual Property Parallel Workers
        ttk.Label(performance_section, text="Individual Property Workers:", style='Heading.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.max_workers_var = tk.IntVar(value=3)
        workers_spinbox = ttk.Spinbox(performance_section, from_=1, to=8, textvariable=self.max_workers_var, width=10)
        workers_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        self.create_tooltip(workers_spinbox, "Number of browser windows working simultaneously for individual property scraping.")

        # Page Scraping Concurrent Control
        ttk.Label(performance_section, text="Page Scraping Mode:", style='Heading.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.page_concurrent_var = tk.BooleanVar(value=False)
        page_concurrent_check = ttk.Checkbutton(performance_section, text="Enable Concurrent Page Scraping", variable=self.page_concurrent_var)
        page_concurrent_check.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        self.create_tooltip(page_concurrent_check, "Enable parallel processing for listing pages (experimental - may trigger bot detection)")

        # Memory optimization
        self.memory_optimization_var = tk.BooleanVar(value=True)
        memory_check = ttk.Checkbutton(performance_section, text="Memory Optimization", variable=self.memory_optimization_var)
        memory_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        self.create_tooltip(memory_check, "Reduces memory usage during scraping. Recommended for long scraping sessions.")

        # === BROWSER SPEED SETTINGS SECTION ===
        browser_section = ttk.LabelFrame(parent, text="🌐 Browser Speed Settings", padding="15")
        browser_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        browser_section.columnconfigure(1, weight=1)
        current_row += 1

        # Page Load Strategy
        ttk.Label(browser_section, text="Page Loading Speed:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.page_load_strategy_var = tk.StringVar(value="normal")
        strategy_combo = ttk.Combobox(browser_section, textvariable=self.page_load_strategy_var, 
                                    values=["normal", "eager", "none"], state="readonly", width=12)
        strategy_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        self.create_tooltip(strategy_combo, "How long to wait for pages to load. 'Normal' = wait for everything (slower but safer), 'Eager' = faster loading, 'None' = fastest but may miss some content.")

        # Disable Images
        self.disable_images_var = tk.BooleanVar(value=True)
        images_check = ttk.Checkbutton(browser_section, text="Skip Images (Faster Loading)", variable=self.disable_images_var)
        images_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        self.create_tooltip(images_check, "Don't load property images. Makes scraping much faster and saves internet data. Property image links are still collected.")

        # Disable CSS
        self.disable_css_var = tk.BooleanVar(value=False)
        css_check = ttk.Checkbutton(browser_section, text="Skip Styling (CSS)", variable=self.disable_css_var)
        css_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        self.create_tooltip(css_check, "Don't load website styling. Makes pages load faster but may affect data extraction accuracy.")

        # Disable JavaScript
        self.disable_js_var = tk.BooleanVar(value=False)
        js_check = ttk.Checkbutton(browser_section, text="Skip JavaScript", variable=self.disable_js_var)
        js_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        self.create_tooltip(js_check, "Don't run website scripts. Fastest option but may miss some property data that loads dynamically.")

        # === PROPERTY FILTERING SECTION ===
        filtering_section = ttk.LabelFrame(parent, text="🔍 Property Filtering", padding="15")
        filtering_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        filtering_section.columnconfigure(1, weight=1)
        current_row += 1

        # Enable filtering checkbox
        self.enable_filtering_var = tk.BooleanVar(value=False)
        enable_filter_check = ttk.Checkbutton(filtering_section, text="Enable Property Filtering",
                                            variable=self.enable_filtering_var,
                                            command=self.toggle_filtering_options)
        enable_filter_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # Price range filtering
        price_frame = ttk.Frame(filtering_section)
        price_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(2, 0))
        price_frame.columnconfigure(1, weight=1)

        ttk.Label(price_frame, text="Price Range (Lakhs):", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)
        price_range_frame = ttk.Frame(price_frame)
        price_range_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        self.price_min_var = tk.StringVar()
        self.price_max_var = tk.StringVar()

        ttk.Entry(price_range_frame, textvariable=self.price_min_var, width=8, state='disabled').grid(row=0, column=0)
        ttk.Label(price_range_frame, text=" - ").grid(row=0, column=1)
        ttk.Entry(price_range_frame, textvariable=self.price_max_var, width=8, state='disabled').grid(row=0, column=2)

        # Area range filtering
        area_frame = ttk.Frame(filtering_section)
        area_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        area_frame.columnconfigure(1, weight=1)

        ttk.Label(area_frame, text="Area Range (Sq.Ft):", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)
        area_range_frame = ttk.Frame(area_frame)
        area_range_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        self.area_min_var = tk.StringVar()
        self.area_max_var = tk.StringVar()

        ttk.Entry(area_range_frame, textvariable=self.area_min_var, width=8, state='disabled').grid(row=0, column=0)
        ttk.Label(area_range_frame, text=" - ").grid(row=0, column=1)
        ttk.Entry(area_range_frame, textvariable=self.area_max_var, width=8, state='disabled').grid(row=0, column=2)

        # BHK filtering
        bhk_frame = ttk.Frame(filtering_section)
        bhk_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Label(bhk_frame, text="BHK Types:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)

        bhk_options_frame = ttk.Frame(bhk_frame)
        bhk_options_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        self.bhk_vars = {}
        bhk_options = ['1', '2', '3', '4', '4+']
        for i, bhk in enumerate(bhk_options):
            var = tk.BooleanVar()
            self.bhk_vars[bhk] = var
            ttk.Checkbutton(bhk_options_frame, text=f"{bhk} BHK", variable=var, state='disabled').grid(row=0, column=i, padx=(0, 10))

        # Store filtering widgets for enabling/disabling
        self.filtering_widgets = [
            price_range_frame.winfo_children()[0],  # price min entry
            price_range_frame.winfo_children()[2],  # price max entry
            area_range_frame.winfo_children()[0],   # area min entry
            area_range_frame.winfo_children()[2],   # area max entry
        ] + [child for child in bhk_options_frame.winfo_children() if isinstance(child, ttk.Checkbutton)]

        # === ACTION SECTION ===
        action_section = ttk.LabelFrame(parent, text="[TARGET] Actions", 
                                      padding="25", style='Modern.TLabelframe')
        action_section.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(25, 15))
        action_section.columnconfigure(0, weight=1)
        current_row += 1

        # Enhanced Start/Stop scraping buttons - large and prominent
        main_action_frame = ttk.Frame(action_section)
        main_action_frame.pack(fill=tk.X, pady=(0, 20))
        main_action_frame.columnconfigure(0, weight=3)
        main_action_frame.columnconfigure(1, weight=1)

        self.start_button = ttk.Button(main_action_frame, text="[ROCKET] Ready to Start Scraping",
                                     command=self.start_scraping, style='Primary.TButton')
        self.start_button.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15), ipady=8)

        self.stop_btn = ttk.Button(main_action_frame, text="⏹️ Stop Scraping",
                                 command=self.stop_scraping, state='disabled', style='Danger.TButton')
        self.stop_btn.grid(row=0, column=1, sticky=(tk.W, tk.E), ipady=8)

        # Enhanced quick action buttons with better spacing
        button_frame = ttk.Frame(action_section)
        button_frame.pack(fill=tk.X)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)

        ttk.Button(button_frame, text="📁 Open Output Folder",
                  command=self.open_output_folder, style='Secondary.TButton').grid(row=0, column=0, padx=(0, 8), sticky=(tk.W, tk.E), ipady=4)

        ttk.Button(button_frame, text="📊 Advanced Dashboard",
                  command=self.open_advanced_dashboard, style='Secondary.TButton').grid(row=0, column=1, padx=8, sticky=(tk.W, tk.E), ipady=4)

        ttk.Button(button_frame, text="🔄 Reset Settings",
                  command=self.reset_settings, style='Secondary.TButton').grid(row=0, column=2, padx=8, sticky=(tk.W, tk.E), ipady=4)

        ttk.Button(button_frame, text="[SAVE] Save Config",
                  command=self.save_config, style='Success.TButton').grid(row=0, column=2, padx=(8, 0), sticky=(tk.W, tk.E), ipady=4)

        # Add bottom padding to ensure all content is scrollable
        ttk.Frame(parent, height=30).grid(row=current_row, column=0)
        current_row += 1

        # Force scroll region update after all widgets are created
        self.root.after(200, self.update_scroll_region)

        # Initialize scraped count
        self.root.after(500, self.refresh_scraped_count)

    def update_scroll_region(self):
        """Force update of scroll region to ensure all content is accessible"""
        try:
            if hasattr(self, 'scrollable_panel'):
                self.scrollable_panel.update_scroll_region()
        except Exception as e:
            print(f"Warning: Could not update scroll region: {e}")

    def toggle_individual_delay_settings(self):
        """Individual delay settings are now always visible - this function is deprecated"""
        # Individual delay settings are now always visible in the timing section
        pass

    def on_individual_pages_changed(self):
        """Handle individual pages checkbox change"""
        self.toggle_individual_delay_settings()
        self.update_individual_pages_info()

    def update_individual_pages_info(self):
        """Update individual pages information text"""
        if self.individual_pages_var.get():
            self.individual_info_var.set("⚠️ Individual page scraping will significantly increase scraping time but provides detailed amenities, floor plans, and neighborhood data.")
        else:
            self.individual_info_var.set("ℹ️ Using listing page data only (recommended for faster scraping)")

    def on_individual_mode_changed(self, event=None):
        """Handle individual scraping mode change"""
        self.update_individual_mode_description()

    def update_individual_mode_description(self):
        """Update individual mode description"""
        mode = self.individual_mode_var.get()
        descriptions = {
            'with_listing': "🔄 Standard Mode: First scrape listing pages, then individual property details",
            'individual_only': "🏠 Individual Only: Skip listing scraping, only scrape individual property pages from existing URLs",
            'skip_individual': "⚡ Listing Only: Skip individual property scraping, only get listing page data"
        }
        self.individual_mode_desc_var.set(descriptions.get(mode, "Unknown mode"))

    def refresh_scraped_count(self):
        """Refresh the count of already scraped individual properties"""
        try:
            # Check for existing CSV files with individual property data
            import glob
            import pandas as pd

            csv_files = glob.glob("magicbricks_*.csv")
            total_individual = 0

            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    # Count rows that have individual property data (non-empty description or amenities)
                    individual_rows = df[
                        (df['description'].notna() & (df['description'] != '')) |
                        (df['amenities'].notna() & (df['amenities'] != ''))
                    ]
                    total_individual += len(individual_rows)
                except Exception:
                    continue

            self.scraped_count_var.set(f"{total_individual} properties with individual details")

        except Exception as e:
            self.scraped_count_var.set(f"Error checking: {str(e)}")

    def get_individual_scraping_config(self):
        """Get configuration for individual property scraping"""
        config = {
            'mode': self.individual_mode_var.get(),
            'max_count': int(self.individual_count_var.get()) if self.individual_count_var.get().isdigit() else 0,
            'force_rescrape': self.force_rescrape_var.get(),
            'enabled': self.individual_pages_var.get()
        }
        return config

    def get_scraping_config(self):
        """Get complete scraping configuration from GUI"""
        try:
            config = {
                'city': self.selected_cities[0] if self.selected_cities else 'gurgaon',
                'selected_cities': self.selected_cities,
                'mode': self.mode_var.get(),
                'max_pages': int(self.max_pages_var.get()) if self.max_pages_var.get().isdigit() else 100,
                'incremental_enabled': self.incremental_var.get(),
                'page_delay': int(self.delay_var.get()),
                'individual_delay_min': int(self.individual_delay_min_var.get()),
                'individual_delay_max': int(self.individual_delay_max_var.get()),
                'batch_break_delay': int(self.batch_break_var.get()),
                'batch_size': int(self.batch_size_var.get()),
                'max_retries': int(self.retry_var.get()),
                'export_csv': self.export_csv_var.get(),
                'export_json': self.export_json_var.get(),
                'export_excel': self.export_excel_var.get(),
                'individual_pages': self.individual_pages_var.get(),
                'output_directory': self.config.get('output_directory', 'output')
            }
            return config
        except Exception as e:
            # Return default config if there's an error
            return {
                'city': 'gurgaon',
                'mode': 'full',
                'max_pages': 100,
                'page_delay': 3,
                'individual_delay_min': 3,
                'individual_delay_max': 8,
                'batch_break_delay': 15,
                'batch_size': 10,
                'max_retries': 2
            }

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        import os
        import subprocess
        import platform

        output_dir = self.output_dir_var.get()
        if not os.path.exists(output_dir):
            messagebox.showwarning("Warning", f"Output directory does not exist: {output_dir}")
            return

        try:
            if platform.system() == "Windows":
                os.startfile(output_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", output_dir])
            else:  # Linux
                subprocess.run(["xdg-open", output_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open output folder: {str(e)}")

    def open_advanced_dashboard(self):
        """Open the advanced dashboard window"""
        try:
            from advanced_dashboard import AdvancedDashboard

            # Check if dashboard is already open
            if hasattr(self, 'dashboard_window') and self.dashboard_window and self.dashboard_window.winfo_exists():
                self.dashboard_window.lift()
                self.dashboard_window.focus()
                return

            # Create new dashboard
            dashboard = AdvancedDashboard(parent=self.root)
            self.dashboard_window = dashboard.root

            self.log_message("Advanced Dashboard opened", 'INFO')

        except ImportError:
            messagebox.showerror("Error", "Advanced Dashboard module not found. Please ensure advanced_dashboard.py is available.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Advanced Dashboard: {str(e)}")
            self.log_message(f"Dashboard error: {str(e)}", 'ERROR')

    def reset_settings(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            # Reset to default values
            self.config = {
                'city': 'gurgaon',
                'mode': ScrapingMode.INCREMENTAL,
                'max_pages': 100,
                'headless': True,
                'output_directory': str(Path.cwd()),
                'incremental_enabled': True,
                'page_delay': 3,
                'max_retries': 2,
                'export_json': False,
                'export_excel': False,
                'individual_pages': False
            }

            # Update GUI elements
            self.mode_var.set(self.config['mode'].value)
            self.max_pages_var.set(str(self.config['max_pages']))
            self.output_dir_var.set(self.config['output_directory'])
            self.headless_var.set(self.config['headless'])
            self.incremental_var.set(self.config['incremental_enabled'])
            self.delay_var.set(str(self.config['page_delay']))
            self.retry_var.set(str(self.config['max_retries']))
            self.export_json_var.set(self.config['export_json'])
            self.export_excel_var.set(self.config['export_excel'])
            self.individual_pages_var.set(self.config['individual_pages'])

            # Update dependent elements
            self.update_mode_description()
            self.toggle_individual_delay_settings()
            self.update_individual_pages_info()

            messagebox.showinfo("Settings Reset", "All settings have been reset to defaults.")

    def save_config(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'city': self.selected_cities[0] if self.selected_cities else 'gurgaon',
                'mode': self.mode_var.get(),
                'max_pages': int(self.max_pages_var.get()),
                'headless': self.headless_var.get(),
                'output_directory': self.output_dir_var.get(),
                'incremental_enabled': self.incremental_var.get(),
                'page_delay': int(self.delay_var.get()),
                'max_retries': int(self.retry_var.get()),
                'export_json': self.export_json_var.get(),
                'export_excel': self.export_excel_var.get(),
                'individual_pages': self.individual_pages_var.get(),
                'individual_delay_min': int(self.individual_delay_min_var.get()),
                'individual_delay_max': int(self.individual_delay_max_var.get()),
                'selected_cities': self.selected_cities
            }

            config_file = Path('magicbricks_gui_config.json')
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)

            messagebox.showinfo("Configuration Saved", f"Configuration saved to {config_file}")

        except Exception as e:
            messagebox.showerror("Error", f"Could not save configuration: {str(e)}")
        
        # Scraping mode
        ttk.Label(control_frame, text="Scraping Mode:", style='Heading.TLabel').grid(row=current_row, column=0, sticky=tk.W, pady=(0, 5))
        self.mode_var = tk.StringVar(value=self.config['mode'].value)
        mode_combo = ttk.Combobox(control_frame, textvariable=self.mode_var, width=20)
        mode_combo['values'] = ('incremental', 'full', 'conservative', 'date_range', 'custom')
        mode_combo.grid(row=current_row, column=1, sticky=(tk.W, tk.E), pady=(0, 15))
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_changed)
        current_row += 1
        
        # Mode description
        self.mode_desc_var = tk.StringVar()
        self.update_mode_description()
        mode_desc_label = ttk.Label(control_frame, textvariable=self.mode_desc_var, style='Info.TLabel', wraplength=300)
        mode_desc_label.grid(row=current_row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        current_row += 1
        
        # Max pages
        ttk.Label(control_frame, text="Max Pages:", style='Heading.TLabel').grid(row=current_row, column=0, sticky=tk.W, pady=(0, 5))
        self.max_pages_var = tk.StringVar(value=str(self.config['max_pages']))
        max_pages_entry = ttk.Entry(control_frame, textvariable=self.max_pages_var, width=10)
        max_pages_entry.grid(row=current_row, column=1, sticky=tk.W, pady=(0, 15))
        current_row += 1
        
        # Output directory
        ttk.Label(control_frame, text="Output Directory:", style='Heading.TLabel').grid(row=current_row, column=0, sticky=tk.W, pady=(0, 5))
        output_frame = ttk.Frame(control_frame)
        output_frame.grid(row=current_row, column=1, sticky=(tk.W, tk.E), pady=(0, 15))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_dir_var = tk.StringVar(value=self.config['output_directory'])
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var)
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(output_frame, text="Browse", command=self.browse_output_directory)
        browse_btn.grid(row=0, column=1)
        current_row += 1
        
        # Advanced options
        advanced_frame = ttk.LabelFrame(control_frame, text="Advanced Options", padding="10")
        advanced_frame.grid(row=current_row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))
        advanced_frame.columnconfigure(1, weight=1)
        current_row += 1

        # Headless mode
        self.headless_var = tk.BooleanVar(value=self.config['headless'])
        headless_check = ttk.Checkbutton(advanced_frame, text="Headless Mode (faster, no browser window)", variable=self.headless_var)
        headless_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        # Incremental enabled
        self.incremental_var = tk.BooleanVar(value=self.config['incremental_enabled'])
        incremental_check = ttk.Checkbutton(advanced_frame, text="Enable Incremental Scraping (60-75% time savings)", variable=self.incremental_var)
        incremental_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        # Individual property pages scraping (use existing variable, don't recreate)
        if not hasattr(self, 'individual_pages_var'):
            self.individual_pages_var = tk.BooleanVar(value=False)
        individual_check = ttk.Checkbutton(advanced_frame, text="Include Individual Property Details (⚠️ 10x slower)",
                                         variable=self.individual_pages_var, command=self.on_individual_pages_changed)
        individual_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        # Individual pages warning/info
        self.individual_info_var = tk.StringVar()
        self.update_individual_pages_info()
        individual_info_label = ttk.Label(advanced_frame, textvariable=self.individual_info_var,
                                        style='Warning.TLabel', wraplength=400)
        individual_info_label.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Export format options
        export_frame = ttk.LabelFrame(advanced_frame, text="Export Formats", padding="10")
        export_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 10))
        export_frame.columnconfigure(0, weight=1)

        # CSV and Database are mandatory
        ttk.Label(export_frame, text="Mandatory: CSV + Database", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)

        # Optional export formats
        ttk.Label(export_frame, text="Optional Formats:", font=('TkDefaultFont', 9)).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # JSON export option
        self.export_json_var = tk.BooleanVar(value=False)
        json_check = ttk.Checkbutton(export_frame, text="JSON (structured data)", variable=self.export_json_var)
        json_check.grid(row=2, column=0, sticky=tk.W, pady=(2, 0))

        # Excel export option
        self.export_excel_var = tk.BooleanVar(value=False)
        excel_check = ttk.Checkbutton(export_frame, text="Excel (multi-sheet with summary)", variable=self.export_excel_var)
        excel_check.grid(row=3, column=0, sticky=tk.W, pady=(2, 0))

        # Delay settings
        delay_frame = ttk.Frame(advanced_frame)
        delay_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        delay_frame.columnconfigure(1, weight=1)

        ttk.Label(delay_frame, text="Page Delay (seconds):").grid(row=0, column=0, sticky=tk.W)
        self.delay_var = tk.StringVar(value="3")
        delay_spin = ttk.Spinbox(delay_frame, from_=1, to=10, textvariable=self.delay_var, width=10)
        delay_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Retry settings
        retry_frame = ttk.Frame(advanced_frame)
        retry_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 15))
        retry_frame.columnconfigure(1, weight=1)

        ttk.Label(retry_frame, text="Max Retries:").grid(row=0, column=0, sticky=tk.W)
        self.retry_var = tk.StringVar(value="3")
        retry_spin = ttk.Spinbox(retry_frame, from_=1, to=10, textvariable=self.retry_var, width=10)
        retry_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Advanced delay configurations
        delay_config_frame = ttk.LabelFrame(advanced_frame, text="Advanced Delay Settings", padding="10")
        delay_config_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        delay_config_frame.columnconfigure(1, weight=1)

        # Individual page delay range (use existing variables from main timing section)
        ttk.Label(delay_config_frame, text="Individual Page Delay (min-max):").grid(row=0, column=0, sticky=tk.W)
        individual_delay_frame = ttk.Frame(delay_config_frame)
        individual_delay_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Use existing variables instead of creating new ones
        if not hasattr(self, 'individual_delay_min_var'):
            self.individual_delay_min_var = tk.StringVar(value="3")
        if not hasattr(self, 'individual_delay_max_var'):
            self.individual_delay_max_var = tk.StringVar(value="8")

        ttk.Spinbox(individual_delay_frame, from_=1, to=30, textvariable=self.individual_delay_min_var, width=5).grid(row=0, column=0)
        ttk.Label(individual_delay_frame, text=" - ").grid(row=0, column=1)
        ttk.Spinbox(individual_delay_frame, from_=1, to=30, textvariable=self.individual_delay_max_var, width=5).grid(row=0, column=2)
        ttk.Label(individual_delay_frame, text=" seconds").grid(row=0, column=3)

        # Batch break delay (use existing variable)
        ttk.Label(delay_config_frame, text="Batch Break Delay:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        if not hasattr(self, 'batch_break_var'):
            self.batch_break_var = tk.StringVar(value="15")
        ttk.Spinbox(delay_config_frame, from_=5, to=60, textvariable=self.batch_break_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))




        
        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=current_row, column=0, columnspan=2, pady=(20, 0))
        
        self.start_btn = ttk.Button(button_frame, text="[ROCKET] Start Scraping", command=self.start_scraping, style='Action.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop Scraping", command=self.stop_scraping, state='disabled', style='Warning.TButton')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_config_btn = ttk.Button(button_frame, text="[SAVE] Save Config", command=self.save_configuration)
        self.save_config_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.recommend_btn = ttk.Button(button_frame, text="[TARGET] Get Recommendations", command=self.get_mode_recommendations)
        self.recommend_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.schedule_btn = ttk.Button(button_frame, text="⏰ Schedule", command=self.open_scheduler)
        self.schedule_btn.pack(side=tk.LEFT)
    
    def create_monitoring_panel(self, parent):
        """Create modern monitoring panel with progress and logs"""

        # Monitoring panel container with modern styling
        monitor_container = ttk.LabelFrame(parent, text="📊 Scraping Progress & Monitoring", 
                                         padding="20", style='Modern.TLabelframe')
        monitor_container.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        monitor_container.columnconfigure(0, weight=1)
        monitor_container.rowconfigure(2, weight=1)

        # === PROGRESS SECTION ===
        progress_section = ttk.LabelFrame(monitor_container, text="📈 Progress", 
                                        padding="20", style='Modern.TLabelframe')
        progress_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_section.columnconfigure(1, weight=1)
        
        # Progress information with modern cards
        ttk.Label(progress_section, text="⚡ Progress:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_section, variable=self.progress_var, 
                                          maximum=100, length=350, style='Modern.Horizontal.TProgressbar')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(15, 0), pady=(0, 8))

        # Progress percentage with enhanced styling
        self.progress_text_var = tk.StringVar(value="0%")
        progress_label = ttk.Label(progress_section, textvariable=self.progress_text_var, 
                                 style='Success.TLabel', font=('Segoe UI', 10, 'bold'))
        progress_label.grid(row=0, column=2, padx=(15, 0))

        # === STATISTICS SECTION ===
        stats_section = ttk.LabelFrame(monitor_container, text="📊 Statistics", 
                                     padding="20", style='Modern.TLabelframe')
        stats_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        stats_section.columnconfigure(0, weight=1)
        stats_section.columnconfigure(1, weight=1)
        stats_section.columnconfigure(2, weight=1)

        # Create modern statistics display with enhanced cards
        self.stats_labels = {}
        stats_info = [
            ('session_id', '🆔 Session ID:', 'N/A'),
            ('mode', '⚙️ Mode:', 'Not Started'),
            ('current_phase', '🔄 Current Phase:', 'Ready'),
            ('pages_scraped', '📄 Pages Scraped:', '0'),
            ('properties_found', '🏠 Properties Found:', '0'),
            ('properties_saved', '[SAVE] Properties Saved:', '0'),
            ('duration', '⏱️ Duration:', '0m 0s'),
            ('estimated_remaining', '⏳ Est. Remaining:', 'N/A'),
            ('scraping_speed', '⚡ Speed:', 'N/A props/min'),
            ('avg_time_per_page', '📊 Avg Time/Page:', 'N/A'),
            ('min_time_per_page', '⚡ Min Time/Page:', 'N/A'),
            ('max_time_per_page', '🐌 Max Time/Page:', 'N/A'),
            ('status', '📊 Status:', 'Ready')
        ]

        for i, (key, label_text, default_value) in enumerate(stats_info):
            row = i // 3
            col = i % 3

            # Create enhanced mini card for each stat
            stat_frame = ttk.Frame(stats_section, style='Card.TFrame')
            stat_frame.grid(row=row, column=col, sticky=(tk.W, tk.E), padx=8, pady=8)
            stat_frame.columnconfigure(0, weight=1)

            # Enhanced label with better typography
            label = ttk.Label(stat_frame, text=label_text, style='Heading.TLabel')
            label.pack(anchor=tk.W, padx=12, pady=(12, 4))

            # Enhanced value label with better styling
            value_label = ttk.Label(stat_frame, text=default_value, style='Info.TLabel',
                                  font=('Segoe UI', 10, 'bold'))
            value_label.pack(anchor=tk.W, padx=12, pady=(0, 12))
            self.stats_labels[key] = value_label

        # === LOG SECTION ===
        log_section = ttk.LabelFrame(monitor_container, text="📝 Scraping Log", 
                                   padding="15", style='Modern.TLabelframe')
        log_section.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_section.columnconfigure(0, weight=1)
        log_section.rowconfigure(0, weight=1)

        # Enhanced log text area with modern styling
        self.log_text = scrolledtext.ScrolledText(log_section, height=12, wrap=tk.WORD,
                                                font=('Consolas', 9), bg='#f8f9fa',
                                                relief='flat', borderwidth=1)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))

        # Enhanced log control buttons with modern styling
        log_btn_frame = ttk.Frame(log_section)
        log_btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        log_btn_frame.columnconfigure(0, weight=1)

        # Left side buttons with enhanced styling
        left_buttons = ttk.Frame(log_btn_frame)
        left_buttons.pack(side=tk.LEFT)

        ttk.Button(left_buttons, text="🗑️ Clear Log", command=self.clear_log,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(left_buttons, text="[SAVE] Save Log", command=self.save_log,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=(0, 8))

        # Right side buttons with enhanced styling
        right_buttons = ttk.Frame(log_btn_frame)
        right_buttons.pack(side=tk.RIGHT)

        ttk.Button(right_buttons, text="📊 View Results", command=self.open_results_viewer,
                  style='Success.TButton').pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(right_buttons, text="🛡️ Error Log", command=self.open_error_log_viewer,
                  style='Secondary.TButton').pack(side=tk.LEFT)
    
    def create_modern_status_bar(self, parent):
        """Create modern status bar with enhanced information"""

        # Status bar container
        status_container = ttk.Frame(parent, style='Card.TFrame')
        status_container.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_container.columnconfigure(1, weight=1)

        # Left side - Status
        status_left = ttk.Frame(status_container)
        status_left.grid(row=0, column=0, sticky=tk.W, padx=15, pady=10)

        ttk.Label(status_left, text="Status:", style='Heading.TLabel').pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="Ready to start scraping")
        status_label = ttk.Label(status_left, textvariable=self.status_var, style='Info.TLabel')
        status_label.pack(side=tk.LEFT, padx=(5, 0))

        # Center - Quick stats
        stats_center = ttk.Frame(status_container)
        stats_center.grid(row=0, column=1, pady=10)

        self.quick_stats_var = tk.StringVar(value="🏙️ Cities: 0 | 📄 Pages: 0 | 🏠 Properties: 0")
        quick_stats_label = ttk.Label(stats_center, textvariable=self.quick_stats_var, style='Info.TLabel')
        quick_stats_label.pack()

        # Right side - Version and time
        status_right = ttk.Frame(status_container)
        status_right.grid(row=0, column=2, sticky=tk.E, padx=15, pady=10)

        version_label = ttk.Label(status_right, text="v2.0 Professional", style='Info.TLabel')
        version_label.pack(side=tk.RIGHT)

        # Current time display
        self.time_var = tk.StringVar()
        time_label = ttk.Label(status_right, textvariable=self.time_var, style='Info.TLabel')
        time_label.pack(side=tk.RIGHT, padx=(0, 10))

        # Update time every second
        self.update_time()

    def update_time(self):
        """Update the current time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_var.set(f"🕐 {current_time}")
        self.root.after(1000, self.update_time)  # Update every second
    
    def _format_duration(self, seconds):
        """Format duration in seconds to human-readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def update_mode_description(self):
        """Update the mode description based on selected mode"""
        
        descriptions = {
            'incremental': '⚡ Smart incremental scraping (60-75% time savings)',
            'full': '🔄 Complete scraping of all properties (100% coverage)',
            'conservative': '🛡️ Extra safe incremental scraping (50-65% savings)',
            'date_range': '📅 Scrape properties within specific date range',
            'custom': '⚙️ User-defined parameters for specific needs'
        }
        
        mode = self.mode_var.get()
        description = descriptions.get(mode, 'Select a scraping mode')
        self.mode_desc_var.set(description)
    
    def on_city_changed(self, event=None):
        """Handle city selection change (legacy method for compatibility)"""
        # This method is kept for compatibility but city selection is now handled by the multi-city system
        pass
    
    def on_mode_changed(self, event=None):
        """Handle mode selection change"""
        mode_str = self.mode_var.get()
        self.config['mode'] = ScrapingMode(mode_str)
        self.update_mode_description()
        self.log_message(f"Scraping mode changed to: {mode_str}")

    def on_individual_pages_changed(self):
        """Handle individual pages option change"""
        self.update_individual_pages_info()
        if self.individual_pages_var.get():
            self.log_message("⚠️ Individual property pages enabled - Scraping will be significantly slower")
        else:
            self.log_message("Individual property pages disabled - Using fast listing-only mode")

    def update_individual_pages_info(self):
        """Update the individual pages information text"""
        if self.individual_pages_var.get():
            info_text = ("⚠️ SLOWER MODE: Will scrape detailed individual property pages including "
                        "amenities, descriptions, builder info, and specifications. "
                        "Expect 5-10x longer scraping time but much more comprehensive data.")
        else:
            info_text = ("[SUCCESS] FAST MODE: Will scrape comprehensive listing data only (22 fields per property). "
                        "Recommended for most users - provides all essential information at maximum speed.")

        self.individual_info_var.set(info_text)

    def toggle_filtering_options(self):
        """Enable/disable filtering options based on checkbox"""
        state = 'normal' if self.enable_filtering_var.get() else 'disabled'

        # Enable/disable filtering widgets
        for widget in self.filtering_widgets:
            widget.configure(state=state)

    def browse_output_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.config['output_directory'])
        if directory:
            self.config['output_directory'] = directory
            self.output_dir_var.set(directory)
            self.log_message(f"Output directory changed to: {directory}")
    
    def save_configuration(self):
        """Save current configuration to file"""
        try:
            config_file = Path('gui_config.json')
            
            # Update config from GUI
            self.update_config_from_gui()
            
            # Convert ScrapingMode to string for JSON serialization
            config_to_save = self.config.copy()
            config_to_save['mode'] = self.config['mode'].value
            
            with open(config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            
            self.log_message(f"Configuration saved to {config_file}")
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            self.log_message(f"Error saving configuration: {str(e)}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def update_config_from_gui(self):
        """Update configuration from GUI values"""
        self.config['selected_cities'] = self.selected_cities
        self.config['city'] = self.selected_cities[0] if self.selected_cities else 'gurgaon'  # Primary city for compatibility
        self.config['mode'] = ScrapingMode(self.mode_var.get())
        self.config['max_pages'] = int(self.max_pages_var.get()) if self.max_pages_var.get().isdigit() else 100
        self.config['output_directory'] = self.output_dir_var.get()
        self.config['headless'] = self.headless_var.get()
        self.config['incremental_enabled'] = self.incremental_var.get()
        
        # Performance settings
        self.config['batch_size'] = int(self.batch_size_var.get()) if hasattr(self, 'batch_size_var') else 10
        self.config['max_workers'] = int(self.max_workers_var.get()) if hasattr(self, 'max_workers_var') else 3
        self.config['memory_optimization'] = self.memory_optimization_var.get() if hasattr(self, 'memory_optimization_var') else True
        
        # Browser optimization settings
        self.config['page_load_strategy'] = self.page_load_strategy_var.get() if hasattr(self, 'page_load_strategy_var') else 'normal'
        self.config['disable_images'] = self.disable_images_var.get() if hasattr(self, 'disable_images_var') else True
        self.config['disable_css'] = self.disable_css_var.get() if hasattr(self, 'disable_css_var') else False
        self.config['disable_javascript'] = self.disable_js_var.get() if hasattr(self, 'disable_js_var') else False
    
    def log_message(self, message: str, level: str = 'INFO'):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # Add to queue for thread-safe GUI updates
        self.message_queue.put(('log', formatted_message))
    
    def update_statistics(self, stats: Dict[str, Any]):
        """Update statistics display with real-time calculations"""

        # Calculate additional metrics
        enhanced_stats = stats.copy()

        # Calculate duration
        if self.scraping_start_time:
            current_time = datetime.now()
            duration = current_time - self.scraping_start_time
            enhanced_stats['duration'] = f"{duration.total_seconds()//60:.0f}m {duration.total_seconds()%60:.0f}s"

            # Calculate scraping speed
            pages_scraped = stats.get('pages_scraped', 0)
            properties_saved = stats.get('properties_saved', 0)

            if duration.total_seconds() > 0:
                properties_per_minute = (properties_saved / duration.total_seconds()) * 60
                enhanced_stats['scraping_speed'] = f"{properties_per_minute:.1f} props/min"

                # Calculate average properties per page
                if pages_scraped > 0:
                    avg_props_per_page = properties_saved / pages_scraped
                    enhanced_stats['avg_properties_per_page'] = f"{avg_props_per_page:.1f}"

                # Estimate remaining time (if we have max_pages)
                max_pages = int(self.max_pages_var.get()) if self.max_pages_var.get().isdigit() else None
                if max_pages and pages_scraped > 0:
                    remaining_pages = max_pages - pages_scraped
                    if remaining_pages > 0 and pages_scraped > 0:
                        avg_time_per_page = duration.total_seconds() / pages_scraped
                        estimated_remaining_seconds = remaining_pages * avg_time_per_page
                        enhanced_stats['estimated_remaining'] = f"{estimated_remaining_seconds//60:.0f}m {estimated_remaining_seconds%60:.0f}s"

        # Store progress history with timing data
        current_time = datetime.now()
        self.progress_history.append({
            'timestamp': current_time,
            'pages_scraped': stats.get('pages_scraped', 0),
            'properties_saved': stats.get('properties_saved', 0)
        })

        # Calculate timing statistics
        if len(self.progress_history) > 1:
            page_times = []
            for i in range(1, len(self.progress_history)):
                prev_entry = self.progress_history[i-1]
                curr_entry = self.progress_history[i]

                if curr_entry['pages_scraped'] > prev_entry['pages_scraped']:
                    time_diff = (curr_entry['timestamp'] - prev_entry['timestamp']).total_seconds()
                    pages_diff = curr_entry['pages_scraped'] - prev_entry['pages_scraped']
                    if pages_diff > 0:
                        time_per_page = time_diff / pages_diff
                        page_times.append(time_per_page)

            if page_times:
                enhanced_stats['avg_time_per_page'] = f"{sum(page_times)/len(page_times):.1f}s"
                enhanced_stats['min_time_per_page'] = f"{min(page_times):.1f}s"
                enhanced_stats['max_time_per_page'] = f"{max(page_times):.1f}s"

        # Keep only last 20 entries for better timing analysis
        if len(self.progress_history) > 20:
            self.progress_history = self.progress_history[-20:]

        self.message_queue.put(('stats', enhanced_stats))
    
    def update_progress(self, progress: float):
        """Update progress bar"""
        self.message_queue.put(('progress', progress))
    
    def update_status(self, status: str):
        """Update status bar"""
        self.message_queue.put(('status', status))
    
    def process_messages(self):
        """Process messages from the queue (thread-safe GUI updates)"""
        try:
            while True:
                message_type, data = self.message_queue.get_nowait()
                
                if message_type == 'log':
                    self.log_text.insert(tk.END, data)
                    self.log_text.see(tk.END)
                
                elif message_type == 'stats':
                    for key, value in data.items():
                        if key in self.stats_labels:
                            self.stats_labels[key].config(text=f"{key.replace('_', ' ').title()}: {value}")
                
                elif message_type == 'progress':
                    self.progress_var.set(data)
                
                elif message_type == 'status':
                    self.status_var.set(data)

                elif message_type == 'error':
                    # Handle error info from error system
                    error_info = data
                    self.log_message(f"[{error_info.severity.value.upper()}] {error_info.title}", 'ERROR')

                    # Show error dialog for critical errors
                    if error_info.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
                        self.show_error_dialog(error_info)
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_messages)
    
    def clear_log(self):
        """Clear the log text"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Save log to file"""
        try:
            log_content = self.log_text.get(1.0, tk.END)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = Path(self.config['output_directory']) / f"scraping_log_{timestamp}.txt"

            with open(log_file, 'w') as f:
                f.write(log_content)

            self.log_message(f"Log saved to {log_file}")
            messagebox.showinfo("Success", f"Log saved to {log_file}")

        except Exception as e:
            self.log_message(f"Error saving log: {str(e)}")
            messagebox.showerror("Error", f"Failed to save log: {str(e)}")

    def get_mode_recommendations(self):
        """Get intelligent mode recommendations based on scraping history"""
        try:
            from user_mode_options import UserModeOptions

            mode_options = UserModeOptions()

            # Get recommendations for current city
            recommendations = mode_options.get_mode_recommendations(self.config['city'])

            # Create recommendation dialog
            self.show_recommendations_dialog(recommendations)

        except Exception as e:
            self.log_message(f"Error getting recommendations: {str(e)}")
            messagebox.showerror("Error", f"Failed to get recommendations: {str(e)}")

    def show_recommendations_dialog(self, recommendations: Dict[str, Any]):
        """Show recommendations in a dialog"""

        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Scraping Mode Recommendations")
        dialog.geometry("500x400")
        dialog.resizable(False, False)

        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()

        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="[TARGET] Intelligent Mode Recommendations", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Primary recommendation
        primary_mode = recommendations.get('primary_recommendation')
        if primary_mode:
            primary_frame = ttk.LabelFrame(main_frame, text="Recommended Mode", padding="15")
            primary_frame.pack(fill=tk.X, pady=(0, 15))

            mode_label = ttk.Label(primary_frame, text=f"Mode: {primary_mode.upper()}", style='Heading.TLabel')
            mode_label.pack(anchor=tk.W)

            # Time savings
            time_savings = recommendations.get('estimated_time_savings', {}).get(primary_mode, 'Unknown')
            savings_label = ttk.Label(primary_frame, text=f"Expected Time Savings: {time_savings}", style='Success.TLabel')
            savings_label.pack(anchor=tk.W, pady=(5, 0))

            # Confidence
            confidence = recommendations.get('confidence_levels', {}).get(primary_mode, 0)
            confidence_label = ttk.Label(primary_frame, text=f"Confidence: {confidence:.1%}", style='Info.TLabel')
            confidence_label.pack(anchor=tk.W, pady=(5, 0))

        # Reasoning
        reasoning_frame = ttk.LabelFrame(main_frame, text="Reasoning", padding="15")
        reasoning_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        reasoning_text = scrolledtext.ScrolledText(reasoning_frame, height=8, wrap=tk.WORD)
        reasoning_text.pack(fill=tk.BOTH, expand=True)

        # Add reasoning
        for reason in recommendations.get('reasoning', []):
            reasoning_text.insert(tk.END, f"• {reason}\n")

        # Alternative recommendations
        alternatives = recommendations.get('alternative_recommendations', [])
        if alternatives:
            reasoning_text.insert(tk.END, f"\nAlternative Options:\n")
            for alt in alternatives:
                time_savings = recommendations.get('estimated_time_savings', {}).get(alt, 'Unknown')
                reasoning_text.insert(tk.END, f"• {alt.upper()}: {time_savings} time savings\n")

        reasoning_text.config(state=tk.DISABLED)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))

        def apply_recommendation():
            if primary_mode:
                self.mode_var.set(primary_mode)
                self.on_mode_changed()
                self.log_message(f"Applied recommended mode: {primary_mode}")
            dialog.destroy()

        apply_btn = ttk.Button(button_frame, text="Apply Recommendation", command=apply_recommendation, style='Action.TButton')
        apply_btn.pack(side=tk.LEFT, padx=(0, 10))

        close_btn = ttk.Button(button_frame, text="Close", command=dialog.destroy)
        close_btn.pack(side=tk.LEFT)

    def open_results_viewer(self):
        """Open the results viewer window"""
        try:
            # Check if we have scraped data
            if not hasattr(self, 'scraper') or not self.scraper or not self.scraper.properties:
                # Try to load from recent CSV files
                self.load_recent_results()
            else:
                # Use current scraper data
                self.show_results_viewer(self.scraper.properties)

        except Exception as e:
            self.log_message(f"Error opening results viewer: {str(e)}")
            messagebox.showerror("Error", f"Failed to open results viewer: {str(e)}")

    def load_recent_results(self):
        """Load recent CSV results for viewing"""
        try:
            # Look for recent CSV files in output directory
            output_dir = Path(self.config['output_directory'])
            csv_files = list(output_dir.glob("magicbricks_*.csv"))

            if not csv_files:
                messagebox.showinfo("No Results", "No scraped data available. Please run a scraping session first.")
                return

            # Sort by modification time (newest first)
            csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Show file selection dialog
            file_dialog = tk.Toplevel(self.root)
            file_dialog.title("Select Results File")
            file_dialog.geometry("600x400")
            file_dialog.transient(self.root)
            file_dialog.grab_set()

            # File list
            frame = ttk.Frame(file_dialog, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(frame, text="Select a results file to view:", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 10))

            # Listbox with scrollbar
            list_frame = ttk.Frame(frame)
            list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
            file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=file_listbox.yview)

            # Populate file list
            for csv_file in csv_files[:10]:  # Show last 10 files
                file_info = f"{csv_file.name} ({csv_file.stat().st_mtime})"
                file_listbox.insert(tk.END, file_info)

            # Buttons
            btn_frame = ttk.Frame(frame)
            btn_frame.pack(pady=(15, 0))

            def load_selected():
                selection = file_listbox.curselection()
                if selection:
                    selected_file = csv_files[selection[0]]
                    file_dialog.destroy()
                    self.load_and_show_csv(selected_file)
                else:
                    messagebox.showwarning("No Selection", "Please select a file to view.")

            ttk.Button(btn_frame, text="Load Selected", command=load_selected, style='Action.TButton').pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(btn_frame, text="Cancel", command=file_dialog.destroy).pack(side=tk.LEFT)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load recent results: {str(e)}")

    def load_and_show_csv(self, csv_file: Path):
        """Load CSV file and show in results viewer"""
        try:
            import pandas as pd

            df = pd.read_csv(csv_file)

            # Convert DataFrame to list of dictionaries
            properties = df.to_dict('records')

            self.show_results_viewer(properties, csv_file.name)
            self.log_message(f"Loaded {len(properties)} properties from {csv_file.name}")

        except Exception as e:
            self.log_message(f"Error loading CSV file: {str(e)}")
            messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")

    def show_results_viewer(self, properties: List[Dict[str, Any]], title_suffix: str = ""):
        """Show the results viewer window"""

        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title(f"Results Viewer {title_suffix}")
        results_window.geometry("1000x700")
        results_window.transient(self.root)

        # Main frame
        main_frame = ttk.Frame(results_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title and summary
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(title_frame, text=f"📊 Results Viewer - {len(properties)} Properties", style='Title.TLabel').pack(side=tk.LEFT)

        # Filter frame
        filter_frame = ttk.LabelFrame(main_frame, text="Filters & Search", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 15))

        # Search box
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(10, 0))

        # Results table frame
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create treeview for results
        columns = ['title', 'price', 'area', 'page_number', 'scraped_at']
        if properties and len(properties) > 0:
            # Use actual columns from data
            columns = list(properties[0].keys())[:8]  # Show first 8 columns

        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        # Configure columns
        for col in columns:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=120, minwidth=80)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Populate treeview
        def populate_tree(filtered_properties=None):
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)

            # Add properties
            data_to_show = filtered_properties if filtered_properties is not None else properties
            for i, prop in enumerate(data_to_show):
                values = []
                for col in columns:
                    value = prop.get(col, 'N/A')
                    # Truncate long values
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    values.append(str(value))
                tree.insert('', tk.END, values=values)

        # Search functionality
        def on_search(*args):
            search_term = search_var.get().lower()
            if not search_term:
                populate_tree()
                return

            filtered = []
            for prop in properties:
                # Search in all string fields
                for value in prop.values():
                    if isinstance(value, str) and search_term in value.lower():
                        filtered.append(prop)
                        break

            populate_tree(filtered)

        search_var.trace('w', on_search)

        # Initial population
        populate_tree()

        # Export buttons
        export_frame = ttk.Frame(main_frame)
        export_frame.pack(pady=(15, 0))

        def export_csv():
            try:
                import pandas as pd
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    title="Export to CSV"
                )
                if filename:
                    df = pd.DataFrame(properties)
                    df.to_csv(filename, index=False)
                    messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

        def export_excel():
            try:
                import pandas as pd
                filename = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    title="Export to Excel"
                )
                if filename:
                    df = pd.DataFrame(properties)
                    df.to_excel(filename, index=False)
                    messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

        def export_json():
            try:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    title="Export to JSON"
                )
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(properties, f, indent=2, default=str)
                    messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

        ttk.Button(export_frame, text="📄 Export CSV", command=export_csv).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="📊 Export Excel", command=export_excel).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(export_frame, text="📋 Export JSON", command=export_json).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(export_frame, text="Close", command=results_window.destroy).pack(side=tk.RIGHT)

    def open_scheduler(self):
        """Open the scheduling interface"""

        # Create scheduler window
        scheduler_window = tk.Toplevel(self.root)
        scheduler_window.title("Scraping Scheduler")
        scheduler_window.geometry("600x500")
        scheduler_window.transient(self.root)
        scheduler_window.grab_set()

        # Main frame
        main_frame = ttk.Frame(scheduler_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="⏰ Scraping Scheduler", style='Title.TLabel').pack(pady=(0, 20))

        # Schedule type selection
        schedule_frame = ttk.LabelFrame(main_frame, text="Schedule Type", padding="15")
        schedule_frame.pack(fill=tk.X, pady=(0, 15))

        schedule_type_var = tk.StringVar(value="preset")

        ttk.Radiobutton(schedule_frame, text="Use Preset Schedule", variable=schedule_type_var, value="preset").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(schedule_frame, text="Custom Schedule", variable=schedule_type_var, value="custom").pack(anchor=tk.W)

        # Preset schedules
        preset_frame = ttk.LabelFrame(main_frame, text="Preset Schedules", padding="15")
        preset_frame.pack(fill=tk.X, pady=(0, 15))

        preset_var = tk.StringVar(value="daily")

        presets = [
            ("daily", "Daily at 2:00 AM (Incremental Mode)"),
            ("weekly", "Weekly on Sunday at 1:00 AM (Conservative Mode)"),
            ("monthly", "Monthly on 1st at 12:00 AM (Full Mode)"),
            ("workdays", "Weekdays at 6:00 AM (Incremental Mode)"),
            ("custom_time", "Custom Time (Current Settings)")
        ]

        for value, text in presets:
            ttk.Radiobutton(preset_frame, text=text, variable=preset_var, value=value).pack(anchor=tk.W, pady=2)

        # Custom schedule
        custom_frame = ttk.LabelFrame(main_frame, text="Custom Schedule", padding="15")
        custom_frame.pack(fill=tk.X, pady=(0, 15))
        custom_frame.columnconfigure(1, weight=1)

        # Time selection
        time_frame = ttk.Frame(custom_frame)
        time_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(time_frame, text="Time:").pack(side=tk.LEFT)

        hour_var = tk.StringVar(value="02")
        minute_var = tk.StringVar(value="00")

        hour_spin = ttk.Spinbox(time_frame, from_=0, to=23, textvariable=hour_var, width=5, format="%02.0f")
        hour_spin.pack(side=tk.LEFT, padx=(10, 5))

        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)

        minute_spin = ttk.Spinbox(time_frame, from_=0, to=59, textvariable=minute_var, width=5, format="%02.0f")
        minute_spin.pack(side=tk.LEFT, padx=(5, 0))

        # Days selection
        days_frame = ttk.Frame(custom_frame)
        days_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(days_frame, text="Days:").pack(anchor=tk.W, pady=(0, 5))

        day_vars = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        days_check_frame = ttk.Frame(days_frame)
        days_check_frame.pack(fill=tk.X)

        for i, day in enumerate(days):
            day_vars[day] = tk.BooleanVar(value=True if day != 'Saturday' and day != 'Sunday' else False)
            ttk.Checkbutton(days_check_frame, text=day[:3], variable=day_vars[day]).grid(row=i//4, column=i%4, sticky=tk.W, padx=(0, 10))

        # Schedule mode
        mode_frame = ttk.Frame(custom_frame)
        mode_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(mode_frame, text="Scraping Mode:").pack(side=tk.LEFT)

        schedule_mode_var = tk.StringVar(value="incremental")
        mode_combo = ttk.Combobox(mode_frame, textvariable=schedule_mode_var, width=15)
        mode_combo['values'] = ('incremental', 'conservative', 'full', 'date_range')
        mode_combo.pack(side=tk.LEFT, padx=(10, 0))

        # Current schedules
        current_frame = ttk.LabelFrame(main_frame, text="Current Schedules", padding="15")
        current_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Schedule list
        schedule_list = tk.Listbox(current_frame, height=6)
        schedule_list.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Add some example schedules
        example_schedules = [
            "Daily 02:00 - Gurgaon Incremental (Active)",
            "Weekly Sun 01:00 - Mumbai Conservative (Active)",
            "Monthly 1st 00:00 - All Cities Full (Inactive)"
        ]

        for schedule in example_schedules:
            schedule_list.insert(tk.END, schedule)

        # Schedule control buttons
        schedule_btn_frame = ttk.Frame(current_frame)
        schedule_btn_frame.pack(pady=(10, 0))

        def create_schedule():
            try:
                # Get schedule configuration
                if schedule_type_var.get() == "preset":
                    preset = preset_var.get()
                    schedule_config = self.get_preset_schedule_config(preset)
                else:
                    # Custom schedule
                    selected_days = [day for day, var in day_vars.items() if var.get()]
                    schedule_config = {
                        'type': 'custom',
                        'time': f"{hour_var.get()}:{minute_var.get()}",
                        'days': selected_days,
                        'mode': schedule_mode_var.get(),
                        'city': self.config['city']
                    }

                # Save schedule (in a real implementation, this would integrate with a task scheduler)
                self.save_schedule(schedule_config)

                # Update schedule list
                schedule_desc = self.format_schedule_description(schedule_config)
                schedule_list.insert(tk.END, schedule_desc)

                messagebox.showinfo("Success", "Schedule created successfully!\n\nNote: This is a demonstration. In a production version, this would integrate with Windows Task Scheduler or a similar service.")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to create schedule: {str(e)}")

        def delete_schedule():
            selection = schedule_list.curselection()
            if selection:
                schedule_list.delete(selection[0])
                messagebox.showinfo("Success", "Schedule deleted successfully!")
            else:
                messagebox.showwarning("No Selection", "Please select a schedule to delete.")

        def toggle_schedule():
            selection = schedule_list.curselection()
            if selection:
                current_text = schedule_list.get(selection[0])
                if "(Active)" in current_text:
                    new_text = current_text.replace("(Active)", "(Inactive)")
                else:
                    new_text = current_text.replace("(Inactive)", "(Active)")

                schedule_list.delete(selection[0])
                schedule_list.insert(selection[0], new_text)
                schedule_list.selection_set(selection[0])

                messagebox.showinfo("Success", "Schedule status toggled!")
            else:
                messagebox.showwarning("No Selection", "Please select a schedule to toggle.")

        ttk.Button(schedule_btn_frame, text="Create Schedule", command=create_schedule, style='Action.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(schedule_btn_frame, text="Delete Selected", command=delete_schedule, style='Warning.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(schedule_btn_frame, text="Toggle Active/Inactive", command=toggle_schedule).pack(side=tk.LEFT, padx=(0, 10))

        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(pady=(15, 0))

        ttk.Button(bottom_frame, text="Close", command=scheduler_window.destroy).pack(side=tk.RIGHT)
        ttk.Button(bottom_frame, text="Help", command=self.show_scheduler_help).pack(side=tk.RIGHT, padx=(0, 10))

    def get_preset_schedule_config(self, preset: str) -> Dict[str, Any]:
        """Get configuration for preset schedule"""

        preset_configs = {
            'daily': {
                'type': 'preset',
                'name': 'Daily Incremental',
                'time': '02:00',
                'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                'mode': 'incremental',
                'city': self.config['city']
            },
            'weekly': {
                'type': 'preset',
                'name': 'Weekly Conservative',
                'time': '01:00',
                'days': ['Sunday'],
                'mode': 'conservative',
                'city': self.config['city']
            },
            'monthly': {
                'type': 'preset',
                'name': 'Monthly Full',
                'time': '00:00',
                'days': ['1st of month'],
                'mode': 'full',
                'city': self.config['city']
            },
            'workdays': {
                'type': 'preset',
                'name': 'Workdays Incremental',
                'time': '06:00',
                'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                'mode': 'incremental',
                'city': self.config['city']
            },
            'custom_time': {
                'type': 'preset',
                'name': 'Custom Time',
                'time': '02:00',
                'days': ['Monday', 'Wednesday', 'Friday'],
                'mode': self.config['mode'].value,
                'city': self.config['city']
            }
        }

        return preset_configs.get(preset, preset_configs['daily'])

    def save_schedule(self, schedule_config: Dict[str, Any]):
        """Save schedule configuration"""
        try:
            # In a real implementation, this would:
            # 1. Save to a schedules.json file
            # 2. Create Windows Task Scheduler entries
            # 3. Set up background service

            schedules_file = Path('schedules.json')

            # Load existing schedules
            schedules = []
            if schedules_file.exists():
                with open(schedules_file, 'r') as f:
                    schedules = json.load(f)

            # Add new schedule
            schedule_config['created_at'] = datetime.now().isoformat()
            schedule_config['active'] = True
            schedules.append(schedule_config)

            # Save schedules
            with open(schedules_file, 'w') as f:
                json.dump(schedules, f, indent=2)

            self.log_message(f"Schedule saved: {schedule_config['name'] if 'name' in schedule_config else 'Custom'}")

        except Exception as e:
            raise Exception(f"Failed to save schedule: {str(e)}")

    def format_schedule_description(self, schedule_config: Dict[str, Any]) -> str:
        """Format schedule configuration into readable description"""

        name = schedule_config.get('name', 'Custom')
        time = schedule_config.get('time', '00:00')
        mode = schedule_config.get('mode', 'incremental')
        city = schedule_config.get('city', 'unknown')

        if len(schedule_config.get('days', [])) == 7:
            days_desc = "Daily"
        elif len(schedule_config.get('days', [])) == 5 and 'Saturday' not in schedule_config.get('days', []):
            days_desc = "Weekdays"
        elif len(schedule_config.get('days', [])) == 1:
            days_desc = schedule_config['days'][0]
        else:
            days_desc = f"{len(schedule_config.get('days', []))} days"

        return f"{days_desc} {time} - {city.title()} {mode.title()} (Active)"

    def show_scheduler_help(self):
        """Show scheduler help dialog"""

        help_text = """
Scheduling Help

PRESET SCHEDULES:
• Daily: Runs incremental scraping every day at 2 AM
• Weekly: Runs conservative scraping every Sunday at 1 AM
• Monthly: Runs full scraping on the 1st of each month at midnight
• Workdays: Runs incremental scraping on weekdays at 6 AM

CUSTOM SCHEDULES:
• Set specific time and days
• Choose scraping mode
• Configure for current city

SCHEDULING MODES:
• Incremental: Fast, 60-75% time savings
• Conservative: Safe, 50-65% time savings
• Full: Complete, 100% coverage
• Date Range: Targeted time periods

NOTES:
• Schedules run in the background
• Results are automatically saved
• Email notifications can be configured
• Multiple schedules can be active

For production deployment, schedules integrate with:
• Windows Task Scheduler
• Background service
• Email notifications
• Error handling and recovery
        """

        messagebox.showinfo("Scheduler Help", help_text)

    def open_city_selector(self):
        """Open the comprehensive city selection dialog"""

        # Create city selector window
        city_window = tk.Toplevel(self.root)
        city_window.title("City Selection - MagicBricks Scraper")
        city_window.geometry("800x600")
        city_window.transient(self.root)
        city_window.grab_set()

        # Main frame
        main_frame = ttk.Frame(city_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        ttk.Label(main_frame, text="🏙️ City Selection", style='Title.TLabel').grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Left panel - Filters
        filter_frame = ttk.LabelFrame(main_frame, text="Filters", padding="15")
        filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        filter_frame.columnconfigure(0, weight=1)

        # Search
        ttk.Label(filter_frame, text="Search:", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=search_var, width=20)
        search_entry.pack(fill=tk.X, pady=(0, 15))

        # Region filter
        ttk.Label(filter_frame, text="Region:", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 5))
        region_var = tk.StringVar(value="All")
        region_combo = ttk.Combobox(filter_frame, textvariable=region_var, width=18)
        region_combo['values'] = ['All'] + [region.value for region in Region]
        region_combo.pack(fill=tk.X, pady=(0, 15))

        # Tier filter
        ttk.Label(filter_frame, text="Tier:", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 5))
        tier_var = tk.StringVar(value="All")
        tier_combo = ttk.Combobox(filter_frame, textvariable=tier_var, width=18)
        tier_combo['values'] = ['All'] + [tier.value for tier in CityTier]
        tier_combo.pack(fill=tk.X, pady=(0, 15))

        # Metro only checkbox
        metro_var = tk.BooleanVar()
        metro_check = ttk.Checkbutton(filter_frame, text="Metro cities only", variable=metro_var)
        metro_check.pack(anchor=tk.W, pady=(0, 15))

        # Quick selections
        ttk.Label(filter_frame, text="Quick Select:", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 5))

        def select_metros():
            metro_cities = self.city_system.get_metro_cities()
            update_city_list([city.code for city in metro_cities])

        def select_tier1():
            tier1_cities = self.city_system.get_cities_by_tier(CityTier.TIER_1)
            update_city_list([city.code for city in tier1_cities])

        def select_top10():
            all_cities = list(self.city_system.cities.values())
            top_cities = sorted([c for c in all_cities if c.is_active], key=lambda x: x.population, reverse=True)[:10]
            update_city_list([city.code for city in top_cities])

        ttk.Button(filter_frame, text="Metro Cities", command=select_metros).pack(fill=tk.X, pady=2)
        ttk.Button(filter_frame, text="Tier 1 Cities", command=select_tier1).pack(fill=tk.X, pady=2)
        ttk.Button(filter_frame, text="Top 10 by Population", command=select_top10).pack(fill=tk.X, pady=2)

        # Middle panel - Available cities
        available_frame = ttk.LabelFrame(main_frame, text="Available Cities", padding="15")
        available_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        available_frame.columnconfigure(0, weight=1)
        available_frame.rowconfigure(0, weight=1)

        # City listbox with scrollbar
        list_frame = ttk.Frame(available_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        city_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=15)
        city_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        city_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=city_listbox.yview)
        city_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        city_listbox.configure(yscrollcommand=city_scrollbar.set)

        # Control buttons
        control_frame = ttk.Frame(available_frame)
        control_frame.pack(pady=(10, 0))

        def add_selected():
            selection = city_listbox.curselection()
            for index in selection:
                city_code = city_codes[index]
                if city_code not in selected_city_codes:
                    selected_city_codes.append(city_code)
            update_selected_display()

        def add_all():
            for city_code in city_codes:
                if city_code not in selected_city_codes:
                    selected_city_codes.append(city_code)
            update_selected_display()

        ttk.Button(control_frame, text="Add Selected →", command=add_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Add All →", command=add_all).pack(side=tk.LEFT)

        # Right panel - Selected cities
        selected_frame = ttk.LabelFrame(main_frame, text="Selected Cities", padding="15")
        selected_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        selected_frame.columnconfigure(0, weight=1)
        selected_frame.rowconfigure(0, weight=1)

        # Selected cities listbox
        selected_list_frame = ttk.Frame(selected_frame)
        selected_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        selected_list_frame.columnconfigure(0, weight=1)
        selected_list_frame.rowconfigure(0, weight=1)

        selected_listbox = tk.Listbox(selected_list_frame, selectmode=tk.MULTIPLE, height=15)
        selected_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        selected_scrollbar = ttk.Scrollbar(selected_list_frame, orient=tk.VERTICAL, command=selected_listbox.yview)
        selected_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        selected_listbox.configure(yscrollcommand=selected_scrollbar.set)

        # Selected control buttons
        selected_control_frame = ttk.Frame(selected_frame)
        selected_control_frame.pack(pady=(10, 0))

        def remove_selected():
            selection = selected_listbox.curselection()
            for index in reversed(selection):  # Remove from end to avoid index issues
                if index < len(selected_city_codes):
                    selected_city_codes.pop(index)
            update_selected_display()

        def remove_all():
            selected_city_codes.clear()
            update_selected_display()

        ttk.Button(selected_control_frame, text="← Remove Selected", command=remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(selected_control_frame, text="← Remove All", command=remove_all).pack(side=tk.LEFT)

        # Initialize data
        city_codes = []
        selected_city_codes = self.selected_cities.copy()

        def update_city_list(filter_codes=None):
            city_listbox.delete(0, tk.END)
            city_codes.clear()

            # Apply filters
            cities_to_show = []

            for city in self.city_system.cities.values():
                if not city.is_active:
                    continue

                # Apply search filter
                search_term = search_var.get().lower()
                if search_term and search_term not in city.name.lower() and search_term not in city.state.lower():
                    continue

                # Apply region filter
                if region_var.get() != "All" and city.region.value != region_var.get():
                    continue

                # Apply tier filter
                if tier_var.get() != "All" and city.tier.value != tier_var.get():
                    continue

                # Apply metro filter
                if metro_var.get() and not city.is_metro:
                    continue

                cities_to_show.append(city)

            # If filter_codes provided, use those instead
            if filter_codes:
                cities_to_show = [self.city_system.cities[code] for code in filter_codes if code in self.city_system.cities]

            # Sort by population (descending)
            cities_to_show.sort(key=lambda x: x.population, reverse=True)

            # Populate listbox
            for city in cities_to_show:
                display_text = f"{city.name}, {city.state} ({city.tier.value}, {city.population:,})"
                city_listbox.insert(tk.END, display_text)
                city_codes.append(city.code)

        def update_selected_display():
            selected_listbox.delete(0, tk.END)

            for city_code in selected_city_codes:
                if city_code in self.city_system.cities:
                    city = self.city_system.cities[city_code]
                    display_text = f"{city.name}, {city.state}"
                    selected_listbox.insert(tk.END, display_text)

            # Update validation info
            validation = self.city_system.validate_city_selection(selected_city_codes)
            validation_text = f"Selected: {len(selected_city_codes)} cities"
            if validation['warnings']:
                validation_text += f" ⚠️ {len(validation['warnings'])} warnings"
            validation_label.config(text=validation_text)

        # Bind filter events
        search_var.trace('w', lambda *args: update_city_list())
        region_var.trace('w', lambda *args: update_city_list())
        tier_var.trace('w', lambda *args: update_city_list())
        metro_var.trace('w', lambda *args: update_city_list())

        # Bottom panel - Validation and actions
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 0))
        bottom_frame.columnconfigure(0, weight=1)

        # Validation info
        validation_label = ttk.Label(bottom_frame, text="Selected: 0 cities", style='Info.TLabel')
        validation_label.pack(side=tk.LEFT)

        # Action buttons
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(side=tk.RIGHT)

        def apply_selection():
            if not selected_city_codes:
                messagebox.showwarning("No Selection", "Please select at least one city.")
                return

            # Validate selection
            validation = self.city_system.validate_city_selection(selected_city_codes)

            if validation['warnings']:
                warning_msg = "Warnings:\n" + "\n".join(validation['warnings'])
                warning_msg += f"\n\nEstimated scraping time: {validation['estimated_time']} minutes"
                warning_msg += f"\nEstimated properties: {validation['total_properties_estimate']:,}"
                warning_msg += "\n\nDo you want to continue?"

                if not messagebox.askyesno("Selection Warnings", warning_msg):
                    return

            # Apply selection
            self.selected_cities = selected_city_codes
            self.update_selected_cities_display()
            city_window.destroy()

            self.log_message(f"Selected {len(selected_city_codes)} cities: {', '.join([self.city_system.cities[code].name for code in selected_city_codes])}")

        def get_recommendations():
            recommendations = self.city_system.get_city_recommendations()
            recommended_codes = [city.code for city in recommendations]
            update_city_list(recommended_codes)

        ttk.Button(button_frame, text="Get Recommendations", command=get_recommendations).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Apply Selection", command=apply_selection, style='Action.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=city_window.destroy).pack(side=tk.LEFT)

        # Initialize displays
        update_city_list()
        update_selected_display()

    def update_selected_cities_display(self):
        """Update the selected cities display in the main GUI"""

        if not self.selected_cities:
            display_text = "No cities selected"
        elif len(self.selected_cities) == 1:
            city = self.city_system.cities.get(self.selected_cities[0])
            display_text = city.name if city else self.selected_cities[0]
        else:
            city_names = []
            for city_code in self.selected_cities[:3]:  # Show first 3
                city = self.city_system.cities.get(city_code)
                if city:
                    city_names.append(city.name)

            display_text = ", ".join(city_names)
            if len(self.selected_cities) > 3:
                display_text += f" + {len(self.selected_cities) - 3} more"

        self.selected_cities_var.set(display_text)

    def on_error_callback(self, error_info):
        """Handle error callback from error handling system"""

        # Add to GUI message queue for thread-safe updates
        self.message_queue.put(('error', error_info))

    def handle_gui_error(self, error: Exception, context: Dict[str, Any] = None, user_action: str = None):
        """Handle errors in GUI with user-friendly display"""

        try:
            # Use error handling system
            error_info = self.error_system.handle_error(error, context, user_action)

            # Show user-friendly error dialog
            self.show_error_dialog(error_info)

            return error_info

        except Exception as e:
            # Fallback error handling
            self.log_message(f"Critical error: {str(e)}", 'ERROR')
            messagebox.showerror("Critical Error", f"A critical error occurred: {str(e)}")

    def show_error_dialog(self, error_info):
        """Show user-friendly error dialog"""

        # Create error dialog
        error_dialog = tk.Toplevel(self.root)
        error_dialog.title(f"Error - {error_info.severity.value.title()}")
        error_dialog.geometry("600x500")
        error_dialog.transient(self.root)
        error_dialog.grab_set()

        # Configure based on severity
        severity_config = {
            'info': {'color': '#17a2b8', 'icon': 'ℹ️'},
            'warning': {'color': '#ffc107', 'icon': '⚠️'},
            'error': {'color': '#dc3545', 'icon': '❌'},
            'critical': {'color': '#6f42c1', 'icon': '🚨'}
        }

        config = severity_config.get(error_info.severity.value, severity_config['error'])

        # Main frame
        main_frame = ttk.Frame(error_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Icon and title
        title_text = f"{config['icon']} {error_info.severity.value.title()} Error"
        title_label = ttk.Label(header_frame, text=title_text, style='Title.TLabel')
        title_label.pack(side=tk.LEFT)

        # Category
        category_label = ttk.Label(header_frame, text=f"Category: {error_info.category.value.title()}", style='Info.TLabel')
        category_label.pack(side=tk.RIGHT)

        # Error message
        message_frame = ttk.LabelFrame(main_frame, text="Error Message", padding="15")
        message_frame.pack(fill=tk.X, pady=(0, 15))

        message_text = tk.Text(message_frame, height=3, wrap=tk.WORD, font=('Arial', 10))
        message_text.pack(fill=tk.X)
        message_text.insert(tk.END, error_info.message)
        message_text.config(state=tk.DISABLED)

        # Suggestion
        suggestion_frame = ttk.LabelFrame(main_frame, text="💡 Suggested Solution", padding="15")
        suggestion_frame.pack(fill=tk.X, pady=(0, 15))

        suggestion_text = tk.Text(suggestion_frame, height=3, wrap=tk.WORD, font=('Arial', 10), bg='#d4edda')
        suggestion_text.pack(fill=tk.X)
        suggestion_text.insert(tk.END, error_info.suggestion)
        suggestion_text.config(state=tk.DISABLED)

        # Details (collapsible)
        details_frame = ttk.LabelFrame(main_frame, text="Technical Details", padding="15")
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        details_text = scrolledtext.ScrolledText(details_frame, height=8, wrap=tk.WORD, font=('Courier', 9))
        details_text.pack(fill=tk.BOTH, expand=True)

        details_content = f"Error Details:\n{error_info.details}\n\n"
        if error_info.context:
            details_content += f"Context:\n{json.dumps(error_info.context, indent=2)}\n\n"
        if error_info.traceback_info:
            details_content += f"Technical Information:\n{error_info.traceback_info}"

        details_text.insert(tk.END, details_content)
        details_text.config(state=tk.DISABLED)

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))

        def copy_error():
            error_dialog.clipboard_clear()
            error_dialog.clipboard_append(details_content)
            messagebox.showinfo("Copied", "Error details copied to clipboard!")

        def view_error_log():
            self.open_error_log_viewer()
            error_dialog.destroy()

        def send_report():
            self.send_error_report(error_info)

        ttk.Button(button_frame, text="📋 Copy Details", command=copy_error).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📊 View Error Log", command=view_error_log).pack(side=tk.LEFT, padx=(0, 10))

        if self.error_system.notification_config.get('email_enabled'):
            ttk.Button(button_frame, text="📧 Send Report", command=send_report).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(button_frame, text="Close", command=error_dialog.destroy, style='Action.TButton').pack(side=tk.RIGHT)

    def open_error_log_viewer(self):
        """Open comprehensive error log viewer"""

        # Create error log window
        log_window = tk.Toplevel(self.root)
        log_window.title("Error Log Viewer")
        log_window.geometry("900x600")
        log_window.transient(self.root)

        # Main frame
        main_frame = ttk.Frame(log_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title and summary
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(title_frame, text="📊 Error Log Viewer", style='Title.TLabel').pack(side=tk.LEFT)

        # Summary
        summary = self.error_system.get_error_summary()
        summary_text = f"Total: {summary['total_errors']} | Recent: {summary['recent_errors']}"
        ttk.Label(title_frame, text=summary_text, style='Info.TLabel').pack(side=tk.RIGHT)

        # Filters
        filter_frame = ttk.LabelFrame(main_frame, text="Filters", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 15))

        # Severity filter
        ttk.Label(filter_frame, text="Severity:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        severity_var = tk.StringVar(value="All")
        severity_combo = ttk.Combobox(filter_frame, textvariable=severity_var, width=12)
        severity_combo['values'] = ['All'] + [s.value for s in ErrorSeverity]
        severity_combo.grid(row=0, column=1, padx=(0, 15))

        # Category filter
        ttk.Label(filter_frame, text="Category:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(filter_frame, textvariable=category_var, width=12)
        category_combo['values'] = ['All'] + [c.value for c in ErrorCategory]
        category_combo.grid(row=0, column=3, padx=(0, 15))

        # Time filter
        ttk.Label(filter_frame, text="Last:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        time_var = tk.StringVar(value="All")
        time_combo = ttk.Combobox(filter_frame, textvariable=time_var, width=10)
        time_combo['values'] = ['All', '1 hour', '6 hours', '24 hours', '7 days']
        time_combo.grid(row=0, column=5, padx=(0, 15))

        # Error list
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview for errors
        columns = ('Time', 'Severity', 'Category', 'Title')
        error_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        # Configure columns
        error_tree.heading('Time', text='Time')
        error_tree.heading('Severity', text='Severity')
        error_tree.heading('Category', text='Category')
        error_tree.heading('Title', text='Title')

        error_tree.column('Time', width=150)
        error_tree.column('Severity', width=80)
        error_tree.column('Category', width=100)
        error_tree.column('Title', width=400)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=error_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=error_tree.xview)
        error_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        error_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Populate error list
        def update_error_list():
            # Clear existing items
            for item in error_tree.get_children():
                error_tree.delete(item)

            # Apply filters
            severity_filter = None if severity_var.get() == "All" else ErrorSeverity(severity_var.get())
            category_filter = None if category_var.get() == "All" else ErrorCategory(category_var.get())

            hours_filter = None
            if time_var.get() != "All":
                time_map = {'1 hour': 1, '6 hours': 6, '24 hours': 24, '7 days': 168}
                hours_filter = time_map.get(time_var.get())

            # Get filtered errors
            filtered_errors = self.error_system.get_filtered_errors(severity_filter, category_filter, hours_filter)

            # Add to treeview
            for error in reversed(filtered_errors):  # Most recent first
                time_str = error.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                severity_str = error.severity.value.upper()
                category_str = error.category.value.title()
                title_str = error.title[:80] + "..." if len(error.title) > 80 else error.title

                # Color coding by severity
                tags = []
                if error.severity == ErrorSeverity.CRITICAL:
                    tags = ['critical']
                elif error.severity == ErrorSeverity.ERROR:
                    tags = ['error']
                elif error.severity == ErrorSeverity.WARNING:
                    tags = ['warning']

                error_tree.insert('', tk.END, values=(time_str, severity_str, category_str, title_str), tags=tags)

        # Configure tags for color coding
        error_tree.tag_configure('critical', background='#f8d7da')
        error_tree.tag_configure('error', background='#f5c6cb')
        error_tree.tag_configure('warning', background='#fff3cd')

        # Bind filter events
        severity_var.trace('w', lambda *args: update_error_list())
        category_var.trace('w', lambda *args: update_error_list())
        time_var.trace('w', lambda *args: update_error_list())

        # Double-click to view details
        def on_error_select(event):
            selection = error_tree.selection()
            if selection:
                item = error_tree.item(selection[0])
                # Find the error by timestamp and title
                time_str = item['values'][0]
                title_str = item['values'][3]

                for error in self.error_system.error_log:
                    if (error.timestamp.strftime('%Y-%m-%d %H:%M:%S') == time_str and
                        error.title.startswith(title_str.replace("...", ""))):
                        self.show_error_dialog(error)
                        break

        error_tree.bind('<Double-1>', on_error_select)

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=(15, 0))

        def clear_log():
            if messagebox.askyesno("Clear Log", "Are you sure you want to clear the error log?"):
                self.error_system.clear_error_log()
                update_error_list()

        def export_log():
            filename = self.error_system.export_error_log()
            if filename:
                messagebox.showinfo("Export Complete", f"Error log exported to {filename}")

        def refresh_log():
            update_error_list()

        ttk.Button(control_frame, text="🔄 Refresh", command=refresh_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="📁 Export", command=export_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🗑️ Clear Log", command=clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="Close", command=log_window.destroy).pack(side=tk.RIGHT)

        # Initial population
        update_error_list()

    def send_error_report(self, error_info):
        """Send error report via email"""

        try:
            # This would trigger the email notification
            self.error_system._send_notification(error_info)
            messagebox.showinfo("Report Sent", "Error report has been sent successfully!")
        except Exception as e:
            messagebox.showerror("Send Failed", f"Failed to send error report: {str(e)}")

    def configure_error_notifications(self):
        """Open error notification configuration dialog"""

        # Create configuration window
        config_window = tk.Toplevel(self.root)
        config_window.title("Error Notification Settings")
        config_window.geometry("500x400")
        config_window.transient(self.root)
        config_window.grab_set()

        # Main frame
        main_frame = ttk.Frame(config_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="📧 Error Notification Settings", style='Title.TLabel').pack(pady=(0, 20))

        # Email settings
        email_frame = ttk.LabelFrame(main_frame, text="Email Configuration", padding="15")
        email_frame.pack(fill=tk.X, pady=(0, 15))
        email_frame.columnconfigure(1, weight=1)

        # Enable email notifications
        email_enabled_var = tk.BooleanVar(value=self.error_system.notification_config.get('email_enabled', False))
        ttk.Checkbutton(email_frame, text="Enable Email Notifications", variable=email_enabled_var).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # SMTP settings
        ttk.Label(email_frame, text="SMTP Server:").grid(row=1, column=0, sticky=tk.W, pady=2)
        smtp_server_var = tk.StringVar(value=self.error_system.notification_config.get('email_smtp_server', 'smtp.gmail.com'))
        ttk.Entry(email_frame, textvariable=smtp_server_var).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(email_frame, text="SMTP Port:").grid(row=2, column=0, sticky=tk.W, pady=2)
        smtp_port_var = tk.StringVar(value=str(self.error_system.notification_config.get('email_smtp_port', 587)))
        ttk.Entry(email_frame, textvariable=smtp_port_var).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(email_frame, text="Username:").grid(row=3, column=0, sticky=tk.W, pady=2)
        username_var = tk.StringVar(value=self.error_system.notification_config.get('email_username', ''))
        ttk.Entry(email_frame, textvariable=username_var).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(email_frame, text="Password:").grid(row=4, column=0, sticky=tk.W, pady=2)
        password_var = tk.StringVar(value=self.error_system.notification_config.get('email_password', ''))
        ttk.Entry(email_frame, textvariable=password_var, show="*").grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)

        # Recipients
        recipients_frame = ttk.LabelFrame(main_frame, text="Recipients", padding="15")
        recipients_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(recipients_frame, text="Email Recipients (one per line):").pack(anchor=tk.W, pady=(0, 5))
        recipients_text = tk.Text(recipients_frame, height=4, width=50)
        recipients_text.pack(fill=tk.X)

        # Load current recipients
        current_recipients = self.error_system.notification_config.get('email_recipients', [])
        recipients_text.insert(tk.END, '\n'.join(current_recipients))

        # Notification levels
        levels_frame = ttk.LabelFrame(main_frame, text="Notification Levels", padding="15")
        levels_frame.pack(fill=tk.X, pady=(0, 15))

        level_vars = {}
        current_levels = self.error_system.notification_config.get('notification_levels', ['error', 'critical'])

        for severity in ErrorSeverity:
            level_vars[severity.value] = tk.BooleanVar(value=severity.value in current_levels)
            ttk.Checkbutton(levels_frame, text=severity.value.title(), variable=level_vars[severity.value]).pack(anchor=tk.W)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))

        def save_config():
            try:
                # Update configuration
                self.error_system.notification_config.update({
                    'email_enabled': email_enabled_var.get(),
                    'email_smtp_server': smtp_server_var.get(),
                    'email_smtp_port': int(smtp_port_var.get()),
                    'email_username': username_var.get(),
                    'email_password': password_var.get(),
                    'email_recipients': [line.strip() for line in recipients_text.get(1.0, tk.END).strip().split('\n') if line.strip()],
                    'notification_levels': [level for level, var in level_vars.items() if var.get()]
                })

                # Save to file
                self.error_system.save_configuration()

                messagebox.showinfo("Success", "Error notification settings saved successfully!")
                config_window.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

        def test_email():
            try:
                # Create test error
                test_error = Exception("Test notification from MagicBricks Scraper")
                error_info = self.error_system.handle_error(test_error, {'test': True}, 'test_notification')

                messagebox.showinfo("Test Sent", "Test notification sent! Check your email.")

            except Exception as e:
                messagebox.showerror("Test Failed", f"Failed to send test email: {str(e)}")

        ttk.Button(button_frame, text="[SAVE] Save Settings", command=save_config, style='Action.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📧 Test Email", command=test_email).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=config_window.destroy).pack(side=tk.RIGHT)
    
    def start_scraping(self):
        """Start the scraping process in a separate thread"""
        if self.is_scraping:
            messagebox.showwarning("Warning", "Scraping is already in progress!")
            return
        
        try:
            # Update configuration
            self.update_config_from_gui()
            
            # Validate configuration
            if not self.validate_configuration():
                return
            
            # Update UI state
            self.is_scraping = True
            self.start_button.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            # Clear previous results and initialize progress tracking
            self.clear_log()
            self.progress_var.set(0)
            self.scraping_start_time = datetime.now()
            self.progress_history = []

            # Start scraping thread
            self.scraping_thread = threading.Thread(target=self.run_scraping, daemon=True)
            self.scraping_thread.start()
            
            self.log_message("Scraping started successfully")
            self.update_status("Scraping in progress...")
            
        except Exception as e:
            self.log_message(f"Error starting scraping: {str(e)}", 'ERROR')
            messagebox.showerror("Error", f"Failed to start scraping: {str(e)}")
            self.reset_ui_state()
    
    def stop_scraping(self):
        """Stop the scraping process"""
        if not self.is_scraping:
            return
        
        self.is_scraping = False
        self.log_message("Stopping scraping...", 'WARNING')
        self.update_status("Stopping scraping...")
        
        # Note: In a real implementation, you'd need to implement proper thread cancellation
        # For now, we'll just update the UI state
        self.reset_ui_state()
    
    def validate_configuration(self) -> bool:
        """Validate the current configuration"""
        try:
            # Validate max pages
            max_pages_str = self.max_pages_var.get()
            if not max_pages_str.isdigit():
                error = ValueError(f"Max pages must be a valid number, got: '{max_pages_str}'")
                self.handle_gui_error(error, {'max_pages': max_pages_str}, 'configuration_validation')
                return False

            max_pages = int(max_pages_str)
            if max_pages <= 0:
                error = ValueError(f"Max pages must be a positive number, got: {max_pages}")
                self.handle_gui_error(error, {'max_pages': max_pages}, 'configuration_validation')
                return False

            # Validate output directory
            output_dir = Path(self.config['output_directory'])
            if not output_dir.exists():
                error = FileNotFoundError(f"Output directory does not exist: {output_dir}")
                self.handle_gui_error(error, {'output_directory': str(output_dir)}, 'configuration_validation')
                return False

            # Validate selected cities
            if not self.selected_cities:
                error = ValueError("No cities selected for scraping")
                self.handle_gui_error(error, {'selected_cities': self.selected_cities}, 'configuration_validation')
                return False

            return True

        except Exception as e:
            self.handle_gui_error(e, {
                'max_pages': self.max_pages_var.get(),
                'output_directory': self.config['output_directory'],
                'selected_cities': self.selected_cities
            }, 'configuration_validation')
            return False
    
    def run_scraping(self):
        """Run the scraping process (called in separate thread)"""
        session_id = None
        try:
            # Initialize scraper
            self.scraper = IntegratedMagicBricksScraper(
                headless=self.config['headless'],
                incremental_enabled=self.config['incremental_enabled']
            )
            
            self.log_message(f"Starting scraping for {self.config['city']} in {self.config['mode'].value} mode")
            
            # Prepare export formats
            export_formats = ['csv']  # CSV is always included
            if self.export_json_var.get():
                export_formats.append('json')
            if self.export_excel_var.get():
                export_formats.append('excel')

            # Prepare custom configuration
            custom_config = {
                'individual_delay_min': int(self.individual_delay_min_var.get()),
                'individual_delay_max': int(self.individual_delay_max_var.get()),
                'batch_break_delay': int(self.batch_break_var.get()),
                'batch_size': int(self.batch_size_var.get()),
                'memory_optimization': self.memory_optimization_var.get(),
                'max_retries': int(self.retry_var.get()),
                'bot_recovery_delay': int(self.bot_delay_var.get()),
                'page_delay_min': int(self.page_delay_min_var.get()),
                'page_delay_max': int(self.page_delay_max_var.get()),

                # Parallel processing configuration
                'concurrent_pages': int(self.max_workers_var.get()),
                'max_concurrent_pages': int(self.max_workers_var.get()),
                'concurrent_enabled': True,

                # Filtering configuration
                'enable_filtering': self.enable_filtering_var.get()
            }

            # Add filtering options if enabled
            if self.enable_filtering_var.get():
                # Price filtering
                price_min = self.price_min_var.get().strip()
                price_max = self.price_max_var.get().strip()
                if price_min or price_max:
                    custom_config['price_filter'] = {
                        'min': float(price_min) * 100000 if price_min else None,  # Convert lakhs to actual value
                        'max': float(price_max) * 100000 if price_max else None
                    }

                # Area filtering
                area_min = self.area_min_var.get().strip()
                area_max = self.area_max_var.get().strip()
                if area_min or area_max:
                    custom_config['area_filter'] = {
                        'min': float(area_min) if area_min else None,
                        'max': float(area_max) if area_max else None
                    }

                # BHK filtering
                selected_bhks = [bhk for bhk, var in self.bhk_vars.items() if var.get()]
                if selected_bhks:
                    custom_config['bhk_filter'] = selected_bhks

            # Create scraper with custom configuration
            self.scraper = IntegratedMagicBricksScraper(custom_config=custom_config)

            # Create progress callback for real-time GUI updates
            def progress_callback(progress_data):
                """Callback function to update GUI with scraping progress"""
                try:
                    # Calculate progress percentage
                    current_page = progress_data.get('current_page', 0)
                    total_pages = progress_data.get('total_pages', 1)
                    progress_percentage = min((current_page / total_pages) * 100, 100)
                    
                    # Update statistics with proper calculations
                    phase = progress_data.get('phase', 'listing_extraction')
                    phase_display = {
                        'listing_extraction': 'Extracting Listings',
                        'individual_scraping': 'Scraping Properties',
                        'processing': 'Processing Data'
                    }.get(phase, 'Processing')

                    stats = {
                        'session_id': progress_data.get('session_id', 'N/A'),
                        'mode': self.config['mode'].value,
                        'current_phase': phase_display,
                        'pages_scraped': current_page,
                        'properties_found': progress_data.get('properties_found', 0),
                        'properties_saved': progress_data.get('properties_found', 0),
                        'status': f"Scraping page {current_page}/{total_pages}"
                    }

                    # Use the proper update_statistics method for enhanced calculations
                    self.update_statistics(stats)
                    self.message_queue.put(('progress', progress_percentage))

                    # Update status with phase information
                    phase = progress_data.get('phase', 'listing_extraction')
                    if phase == 'listing_extraction':
                        status_msg = f"Extracting listings - Page {current_page}/{total_pages}"
                    elif phase == 'individual_scraping':
                        status_msg = f"Scraping individual properties - {current_page}/{total_pages}"
                    else:
                        status_msg = f"Processing - {current_page}/{total_pages}"

                    self.message_queue.put(('status', status_msg))
                    
                except Exception as e:
                    self.log_message(f"Progress callback error: {str(e)}", 'ERROR')
            
            # Note: scraping_start_time already set as datetime.now() in start_scraping()
            
            # Get individual property scraping configuration
            individual_config = self.get_individual_scraping_config()

            # Add individual property configuration to custom config
            custom_config.update({
                'individual_scraping_mode': individual_config['mode'],
                'max_individual_properties': individual_config['max_count'],
                'force_rescrape_individual': individual_config['force_rescrape']
            })

            # Start scraping with enhanced individual property management
            result = self.scraper.scrape_properties_with_incremental(
                city=self.config['city'],
                mode=self.config['mode'],
                max_pages=self.config['max_pages'],
                include_individual_pages=individual_config['enabled'],
                export_formats=export_formats,
                progress_callback=progress_callback,
                force_rescrape_individual=individual_config['force_rescrape']
            )

            # Get session ID for error tracking
            session_id = result.get('session_stats', {}).get('session_id')
            
            if result['success']:
                self.log_message("Scraping completed successfully!", 'SUCCESS')
                
                # Update final statistics
                final_stats = {
                    'session_id': result.get('session_stats', {}).get('session_id', 'N/A'),
                    'mode': self.config['mode'].value,
                    'pages_scraped': result.get('pages_scraped', 0),
                    'properties_found': result.get('session_stats', {}).get('properties_found', 0),
                    'properties_saved': result.get('properties_scraped', 0),
                    'duration': result.get('session_stats', {}).get('duration_formatted', 'N/A'),
                    'status': 'Completed Successfully'
                }
                
                self.update_statistics(final_stats)
                self.update_progress(100)
                self.update_status("Scraping completed successfully!")
                
                # Save results
                if self.scraper.properties:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"magicbricks_{self.config['city']}_{self.config['mode'].value}_{timestamp}.csv"
                    output_path = Path(self.config['output_directory']) / filename
                    
                    df = self.scraper.save_to_csv(str(output_path))
                    if df is not None:
                        self.log_message(f"Results saved to: {output_path}")
                        messagebox.showinfo("Success", f"Scraping completed!\n\nProperties scraped: {len(df)}\nSaved to: {filename}")
                
            else:
                # Handle scraping failure with error system
                error = Exception(result['error'])
                self.handle_gui_error(error, {
                    'city': self.config['city'],
                    'mode': self.config['mode'].value,
                    'max_pages': self.config['max_pages']
                }, 'scraping_execution')

        except Exception as e:
            # Handle unexpected errors with error system
            self.handle_gui_error(e, {
                'city': self.config['city'],
                'mode': self.config['mode'].value,
                'session_id': session_id
            }, 'scraping_execution')
        
        finally:
            # Clean up
            if self.scraper:
                self.scraper.close()
            
            self.reset_ui_state()
    
    def reset_ui_state(self):
        """Reset UI state after scraping"""
        self.is_scraping = False
        self.start_button.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.update_status("Ready to start scraping")
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="#ffffe0", 
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def run(self):
        """Run the GUI application"""
        try:
            self.log_message("MagicBricks GUI Application started")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_message("Application interrupted by user")
        except Exception as e:
            self.log_message(f"Application error: {str(e)}", 'ERROR')
        finally:
            if self.scraper:
                self.scraper.close()


def main():
    """Main function to run the GUI application"""
    try:
        app = MagicBricksGUI()
        app.run()
    except Exception as e:
        print(f"Failed to start GUI application: {str(e)}")


if __name__ == "__main__":
    main()
