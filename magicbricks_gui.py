#!/usr/bin/env python3
"""
MagicBricks Scraper GUI Application
User-friendly interface for non-technical users with complete scraping control and monitoring.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
import json
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
    Modern GUI application for MagicBricks scraper with user-friendly interface
    """
    
    def __init__(self):
        """Initialize the GUI application"""
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("MagicBricks Property Scraper - Professional Edition")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configure style
        self.setup_styles()
        
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
        
        # Configuration
        self.config = {
            'city': 'gurgaon',
            'mode': ScrapingMode.INCREMENTAL,
            'max_pages': 100,
            'headless': True,
            'output_directory': str(Path.cwd()),
            'incremental_enabled': True
        }
        
        # Create GUI components
        self.create_main_interface()

        # Initialize selected cities display
        self.update_selected_cities_display()

        # Start message processing
        self.process_messages()

        print("🎮 MagicBricks GUI Application Initialized")
        print(f"   🏙️ Multi-city system: {len(self.city_system.cities)} cities available")
    
    def setup_styles(self):
        """Setup modern styling for the GUI"""
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Use modern theme
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')
        
        # Custom colors
        bg_color = '#f0f0f0'
        accent_color = '#2196F3'
        success_color = '#4CAF50'
        warning_color = '#FF9800'
        error_color = '#F44336'
        
        # Configure root window
        self.root.configure(bg=bg_color)
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background=bg_color)
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background=bg_color)
        style.configure('Info.TLabel', font=('Arial', 10), background=bg_color)
        style.configure('Success.TLabel', font=('Arial', 10), background=bg_color, foreground=success_color)
        style.configure('Warning.TLabel', font=('Arial', 10), background=bg_color, foreground=warning_color)
        style.configure('Error.TLabel', font=('Arial', 10), background=bg_color, foreground=error_color)
        
        # Button styles
        style.configure('Action.TButton', font=('Arial', 11, 'bold'))
        style.configure('Success.TButton', font=('Arial', 11, 'bold'))
        style.configure('Warning.TButton', font=('Arial', 11, 'bold'))
    
    def create_main_interface(self):
        """Create the main interface layout"""
        
        # Create main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏠 MagicBricks Property Scraper", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="Professional property data extraction with intelligent incremental scraping", style='Info.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30), sticky=tk.W)
        
        # Create left panel (controls)
        self.create_control_panel(main_frame)
        
        # Create right panel (monitoring)
        self.create_monitoring_panel(main_frame)
        
        # Create bottom status bar
        self.create_status_bar(main_frame)
    
    def create_control_panel(self, parent):
        """Create the control panel with scraping options"""
        
        # Control panel frame
        control_frame = ttk.LabelFrame(parent, text="Scraping Configuration", padding="15")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        current_row = 0
        
        # City selection
        city_frame = ttk.Frame(control_frame)
        city_frame.grid(row=current_row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        city_frame.columnconfigure(1, weight=1)

        ttk.Label(city_frame, text="Cities:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Selected cities display
        self.selected_cities_var = tk.StringVar(value="Gurgaon")
        selected_cities_label = ttk.Label(city_frame, textvariable=self.selected_cities_var, style='Info.TLabel', relief='sunken', padding="5")
        selected_cities_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5))

        # City selection button
        select_cities_btn = ttk.Button(city_frame, text="Select Cities", command=self.open_city_selector)
        select_cities_btn.grid(row=0, column=2)

        current_row += 1
        
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

        # Individual property pages scraping
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

        # Delay settings
        delay_frame = ttk.Frame(advanced_frame)
        delay_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        delay_frame.columnconfigure(1, weight=1)

        ttk.Label(delay_frame, text="Page Delay (seconds):").grid(row=0, column=0, sticky=tk.W)
        self.delay_var = tk.StringVar(value="3")
        delay_spin = ttk.Spinbox(delay_frame, from_=1, to=10, textvariable=self.delay_var, width=10)
        delay_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Retry settings
        retry_frame = ttk.Frame(advanced_frame)
        retry_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 15))
        retry_frame.columnconfigure(1, weight=1)

        ttk.Label(retry_frame, text="Max Retries:").grid(row=0, column=0, sticky=tk.W)
        self.retry_var = tk.StringVar(value="3")
        retry_spin = ttk.Spinbox(retry_frame, from_=1, to=10, textvariable=self.retry_var, width=10)
        retry_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=current_row, column=0, columnspan=2, pady=(20, 0))
        
        self.start_btn = ttk.Button(button_frame, text="🚀 Start Scraping", command=self.start_scraping, style='Action.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop Scraping", command=self.stop_scraping, state='disabled', style='Warning.TButton')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_config_btn = ttk.Button(button_frame, text="💾 Save Config", command=self.save_configuration)
        self.save_config_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.recommend_btn = ttk.Button(button_frame, text="🎯 Get Recommendations", command=self.get_mode_recommendations)
        self.recommend_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.schedule_btn = ttk.Button(button_frame, text="⏰ Schedule", command=self.open_scheduler)
        self.schedule_btn.pack(side=tk.LEFT)
    
    def create_monitoring_panel(self, parent):
        """Create the monitoring panel with progress and logs"""
        
        # Monitoring panel frame
        monitor_frame = ttk.LabelFrame(parent, text="Scraping Progress & Monitoring", padding="15")
        monitor_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        monitor_frame.columnconfigure(0, weight=1)
        monitor_frame.rowconfigure(2, weight=1)
        
        # Progress section
        progress_frame = ttk.Frame(monitor_frame)
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(1, weight=1)
        
        # Progress bar
        ttk.Label(progress_frame, text="Progress:", style='Heading.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # Statistics
        stats_frame = ttk.Frame(monitor_frame)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Create statistics labels
        self.stats_labels = {}
        stats_info = [
            ('session_id', 'Session ID: N/A'),
            ('mode', 'Mode: Not Started'),
            ('pages_scraped', 'Pages Scraped: 0'),
            ('properties_found', 'Properties Found: 0'),
            ('properties_saved', 'Properties Saved: 0'),
            ('duration', 'Duration: 0m 0s'),
            ('estimated_remaining', 'Est. Remaining: N/A'),
            ('avg_properties_per_page', 'Avg Props/Page: N/A'),
            ('scraping_speed', 'Speed: N/A props/min'),
            ('status', 'Status: Ready')
        ]

        for i, (key, default_text) in enumerate(stats_info):
            label = ttk.Label(stats_frame, text=default_text, style='Info.TLabel')
            label.grid(row=i//3, column=i%3, sticky=tk.W, padx=(0, 15), pady=2)
            self.stats_labels[key] = label
        
        # Log output
        ttk.Label(monitor_frame, text="Scraping Log:", style='Heading.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        
        self.log_text = scrolledtext.ScrolledText(monitor_frame, height=15, width=60, wrap=tk.WORD)
        self.log_text.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log control buttons
        log_btn_frame = ttk.Frame(monitor_frame)
        log_btn_frame.grid(row=4, column=0, pady=(10, 0))
        
        clear_log_btn = ttk.Button(log_btn_frame, text="Clear Log", command=self.clear_log)
        clear_log_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        save_log_btn = ttk.Button(log_btn_frame, text="Save Log", command=self.save_log)
        save_log_btn.pack(side=tk.LEFT, padx=(0, 10))

        view_results_btn = ttk.Button(log_btn_frame, text="📊 View Results", command=self.open_results_viewer)
        view_results_btn.pack(side=tk.LEFT, padx=(0, 10))

        error_log_btn = ttk.Button(log_btn_frame, text="🛡️ Error Log", command=self.open_error_log_viewer)
        error_log_btn.pack(side=tk.LEFT)
    
    def create_status_bar(self, parent):
        """Create the bottom status bar"""
        
        # Status bar frame
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to start scraping")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Info.TLabel')
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Version info
        version_label = ttk.Label(status_frame, text="v2.0 - Incremental Scraping Edition", style='Info.TLabel')
        version_label.grid(row=0, column=1, sticky=tk.E)
    
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
            info_text = ("✅ FAST MODE: Will scrape comprehensive listing data only (22 fields per property). "
                        "Recommended for most users - provides all essential information at maximum speed.")

        self.individual_info_var.set(info_text)

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

        # Store progress history
        self.progress_history.append({
            'timestamp': datetime.now(),
            'pages_scraped': stats.get('pages_scraped', 0),
            'properties_saved': stats.get('properties_saved', 0)
        })

        # Keep only last 10 entries
        if len(self.progress_history) > 10:
            self.progress_history = self.progress_history[-10:]

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
        title_label = ttk.Label(main_frame, text="🎯 Intelligent Mode Recommendations", style='Title.TLabel')
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

        ttk.Button(button_frame, text="💾 Save Settings", command=save_config, style='Action.TButton').pack(side=tk.LEFT, padx=(0, 10))
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
            self.start_btn.config(state='disabled')
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
            
            # Start scraping with individual pages option
            result = self.scraper.scrape_properties_with_incremental(
                city=self.config['city'],
                mode=self.config['mode'],
                max_pages=self.config['max_pages'],
                include_individual_pages=self.individual_pages_var.get()
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
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.update_status("Ready to start scraping")
    
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
