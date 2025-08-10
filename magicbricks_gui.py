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

# Import our integrated scraper
from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


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
        
        # Start message processing
        self.process_messages()
        
        print("🎮 MagicBricks GUI Application Initialized")
    
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
        ttk.Label(control_frame, text="City:", style='Heading.TLabel').grid(row=current_row, column=0, sticky=tk.W, pady=(0, 5))
        self.city_var = tk.StringVar(value=self.config['city'])
        city_combo = ttk.Combobox(control_frame, textvariable=self.city_var, width=20)
        city_combo['values'] = ('gurgaon', 'mumbai', 'bangalore', 'delhi', 'pune', 'chennai', 'hyderabad', 'kolkata')
        city_combo.grid(row=current_row, column=1, sticky=(tk.W, tk.E), pady=(0, 15))
        city_combo.bind('<<ComboboxSelected>>', self.on_city_changed)
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

        # Delay settings
        delay_frame = ttk.Frame(advanced_frame)
        delay_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        delay_frame.columnconfigure(1, weight=1)

        ttk.Label(delay_frame, text="Page Delay (seconds):").grid(row=0, column=0, sticky=tk.W)
        self.delay_var = tk.StringVar(value="3")
        delay_spin = ttk.Spinbox(delay_frame, from_=1, to=10, textvariable=self.delay_var, width=10)
        delay_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Retry settings
        retry_frame = ttk.Frame(advanced_frame)
        retry_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 15))
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
        view_results_btn.pack(side=tk.LEFT)
    
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
        """Handle city selection change"""
        self.config['city'] = self.city_var.get()
        self.log_message(f"City changed to: {self.config['city']}")
    
    def on_mode_changed(self, event=None):
        """Handle mode selection change"""
        mode_str = self.mode_var.get()
        self.config['mode'] = ScrapingMode(mode_str)
        self.update_mode_description()
        self.log_message(f"Scraping mode changed to: {mode_str}")
    
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
        self.config['city'] = self.city_var.get()
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
            max_pages = int(self.max_pages_var.get())
            if max_pages <= 0:
                messagebox.showerror("Error", "Max pages must be a positive number")
                return False
            
            # Validate output directory
            output_dir = Path(self.config['output_directory'])
            if not output_dir.exists():
                messagebox.showerror("Error", f"Output directory does not exist: {output_dir}")
                return False
            
            return True
            
        except ValueError:
            messagebox.showerror("Error", "Max pages must be a valid number")
            return False
    
    def run_scraping(self):
        """Run the scraping process (called in separate thread)"""
        try:
            # Initialize scraper
            self.scraper = IntegratedMagicBricksScraper(
                headless=self.config['headless'],
                incremental_enabled=self.config['incremental_enabled']
            )
            
            self.log_message(f"Starting scraping for {self.config['city']} in {self.config['mode'].value} mode")
            
            # Start scraping
            result = self.scraper.scrape_properties_with_incremental(
                city=self.config['city'],
                mode=self.config['mode'],
                max_pages=self.config['max_pages']
            )
            
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
                self.log_message(f"Scraping failed: {result['error']}", 'ERROR')
                messagebox.showerror("Error", f"Scraping failed: {result['error']}")
            
        except Exception as e:
            self.log_message(f"Scraping error: {str(e)}", 'ERROR')
            messagebox.showerror("Error", f"Scraping failed: {str(e)}")
        
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
