#!/usr/bin/env python3
"""
Modern, Vibrant GUI Design for MagicBricks Scraper
User-friendly interface designed for non-technical users
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
from datetime import datetime
from typing import Dict, Any


class ModernMagicBricksGUI:
    """
    Modern, colorful, and intuitive GUI for MagicBricks scraper
    Designed specifically for non-technical users
    """
    
    def __init__(self):
        """Initialize the modern GUI"""
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("🏠 MagicBricks Property Scraper - Professional Edition")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Modern color palette - vibrant and professional
        self.colors = {
            # Primary colors - vibrant blues and greens
            'primary': '#2563eb',           # Vibrant blue
            'primary_light': '#3b82f6',     # Light blue
            'primary_dark': '#1d4ed8',      # Dark blue
            'secondary': '#10b981',         # Emerald green
            'secondary_light': '#34d399',   # Light green
            'accent': '#f59e0b',           # Amber
            'accent_light': '#fbbf24',     # Light amber
            
            # Background colors - clean and modern
            'bg_main': '#f8fafc',          # Very light gray-blue
            'bg_card': '#ffffff',          # Pure white
            'bg_sidebar': '#1e293b',       # Dark slate
            'bg_header': '#0f172a',        # Very dark slate
            'bg_success': '#ecfdf5',       # Light green background
            'bg_warning': '#fffbeb',       # Light amber background
            'bg_error': '#fef2f2',         # Light red background
            
            # Text colors
            'text_primary': '#0f172a',     # Very dark
            'text_secondary': '#475569',   # Medium gray
            'text_light': '#94a3b8',       # Light gray
            'text_white': '#ffffff',       # White
            'text_success': '#065f46',     # Dark green
            'text_warning': '#92400e',     # Dark amber
            'text_error': '#991b1b',       # Dark red
            
            # Status colors - bright and clear
            'success': '#10b981',          # Green
            'warning': '#f59e0b',          # Amber
            'error': '#ef4444',            # Red
            'info': '#06b6d4',             # Cyan
            
            # Border and shadow
            'border': '#e2e8f0',           # Light border
            'border_dark': '#cbd5e1',      # Darker border
            'shadow': '#00000015',         # Subtle shadow
        }
        
        # Setup modern styling
        self.setup_vibrant_styles()
        
        # Initialize variables
        self.is_scraping = False
        self.message_queue = queue.Queue()
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to start scraping")
        
        # Configuration
        self.config = {
            'city': 'gurgaon',
            'max_pages': 100,
            'individual_pages': False,
            'export_formats': ['csv', 'database']
        }
        
        # Create the modern interface
        self.create_vibrant_interface()
        
        # Start message processing
        self.process_messages()
    
    def setup_vibrant_styles(self):
        """Setup vibrant, modern styling"""
        
        self.style = ttk.Style()
        
        # Use a modern theme as base
        try:
            self.style.theme_use('clam')
        except:
            self.style.theme_use('default')
        
        # Configure main window background
        self.root.configure(bg=self.colors['bg_main'])
        
        # Header styles - bold and prominent
        self.style.configure('Header.TLabel',
                           font=('Segoe UI', 24, 'bold'),
                           background=self.colors['bg_header'],
                           foreground=self.colors['text_white'],
                           padding=(20, 15))
        
        self.style.configure('Subheader.TLabel',
                           font=('Segoe UI', 14),
                           background=self.colors['bg_header'],
                           foreground=self.colors['primary_light'],
                           padding=(20, 5))
        
        # Card styles - clean and elevated
        self.style.configure('Card.TFrame',
                           background=self.colors['bg_card'],
                           relief='flat',
                           borderwidth=0)
        
        self.style.configure('Card.TLabelframe',
                           background=self.colors['bg_card'],
                           relief='flat',
                           borderwidth=2,
                           lightcolor=self.colors['border'],
                           darkcolor=self.colors['border'])
        
        # Button styles - vibrant and engaging
        self.style.configure('Primary.TButton',
                           font=('Segoe UI', 12, 'bold'),
                           padding=(30, 15),
                           relief='flat',
                           borderwidth=0)
        
        self.style.map('Primary.TButton',
                      background=[('active', self.colors['primary_dark']),
                                ('!active', self.colors['primary'])],
                      foreground=[('active', self.colors['text_white']),
                                ('!active', self.colors['text_white'])])
        
        self.style.configure('Success.TButton',
                           font=('Segoe UI', 11, 'bold'),
                           padding=(25, 12),
                           relief='flat')
        
        self.style.map('Success.TButton',
                      background=[('active', '#059669'),
                                ('!active', self.colors['secondary'])],
                      foreground=[('active', self.colors['text_white']),
                                ('!active', self.colors['text_white'])])
        
        self.style.configure('Warning.TButton',
                           font=('Segoe UI', 11, 'bold'),
                           padding=(25, 12),
                           relief='flat')
        
        self.style.map('Warning.TButton',
                      background=[('active', '#d97706'),
                                ('!active', self.colors['accent'])],
                      foreground=[('active', self.colors['text_white']),
                                ('!active', self.colors['text_white'])])
        
        # Progress bar - vibrant and smooth
        self.style.configure('Modern.Horizontal.TProgressbar',
                           background=self.colors['primary'],
                           troughcolor=self.colors['bg_main'],
                           borderwidth=0,
                           lightcolor=self.colors['primary'],
                           darkcolor=self.colors['primary'])
        
        # Text styles - clear hierarchy
        self.style.configure('Title.TLabel',
                           font=('Segoe UI', 16, 'bold'),
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'])
        
        self.style.configure('Subtitle.TLabel',
                           font=('Segoe UI', 12),
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_secondary'])
        
        self.style.configure('Success.TLabel',
                           font=('Segoe UI', 11, 'bold'),
                           background=self.colors['bg_card'],
                           foreground=self.colors['success'])
        
        self.style.configure('Warning.TLabel',
                           font=('Segoe UI', 11, 'bold'),
                           background=self.colors['bg_card'],
                           foreground=self.colors['warning'])
        
        self.style.configure('Error.TLabel',
                           font=('Segoe UI', 11, 'bold'),
                           background=self.colors['bg_card'],
                           foreground=self.colors['error'])
    
    def create_vibrant_interface(self):
        """Create the vibrant, user-friendly interface"""
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_main'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header section - prominent and welcoming
        self.create_header_section(main_container)
        
        # Content area with sidebar and main panel
        content_frame = tk.Frame(main_container, bg=self.colors['bg_main'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Configure grid
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left sidebar - configuration panel
        self.create_sidebar(content_frame)
        
        # Main panel - monitoring and results
        self.create_main_panel(content_frame)
        
        # Footer - status and controls
        self.create_footer(main_container)
    
    def create_header_section(self, parent):
        """Create prominent header section"""
        
        header_frame = tk.Frame(parent, bg=self.colors['bg_header'], height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg=self.colors['bg_header'])
        header_content.pack(expand=True, fill=tk.BOTH, padx=30, pady=20)
        
        # Title and subtitle
        title_label = ttk.Label(header_content, 
                               text="🏠 MagicBricks Property Scraper",
                               style='Header.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(header_content,
                                  text="Professional real estate data extraction tool - Simple, Fast, Reliable",
                                  style='Subheader.TLabel')
        subtitle_label.pack(anchor=tk.W)
    
    def create_sidebar(self, parent):
        """Create configuration sidebar"""
        
        # Sidebar container
        sidebar_frame = ttk.Frame(parent, style='Card.TFrame', width=350)
        sidebar_frame.grid(row=0, column=0, sticky=(tk.W, tk.N, tk.S), padx=(0, 15))
        sidebar_frame.grid_propagate(False)
        
        # Sidebar content with padding
        sidebar_content = tk.Frame(sidebar_frame, bg=self.colors['bg_card'])
        sidebar_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configuration section
        config_label = ttk.Label(sidebar_content, text="⚙️ Configuration", style='Title.TLabel')
        config_label.pack(anchor=tk.W, pady=(0, 15))
        
        # City selection
        city_frame = tk.Frame(sidebar_content, bg=self.colors['bg_card'])
        city_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(city_frame, text="📍 City:", style='Subtitle.TLabel').pack(anchor=tk.W)
        self.city_var = tk.StringVar(value='gurgaon')
        city_combo = ttk.Combobox(city_frame, textvariable=self.city_var,
                                 values=['gurgaon', 'mumbai', 'delhi', 'bangalore', 'pune'],
                                 state='readonly', font=('Segoe UI', 11))
        city_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Pages selection
        pages_frame = tk.Frame(sidebar_content, bg=self.colors['bg_card'])
        pages_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(pages_frame, text="📄 Maximum Pages:", style='Subtitle.TLabel').pack(anchor=tk.W)
        self.pages_var = tk.StringVar(value='100')
        pages_entry = tk.Entry(pages_frame, textvariable=self.pages_var, 
                              font=('Segoe UI', 11), relief='flat', bd=5)
        pages_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Individual pages option
        individual_frame = tk.Frame(sidebar_content, bg=self.colors['bg_card'])
        individual_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.individual_var = tk.BooleanVar()
        individual_check = tk.Checkbutton(individual_frame,
                                        text="🏠 Include Individual Property Details",
                                        variable=self.individual_var,
                                        bg=self.colors['bg_card'],
                                        fg=self.colors['text_primary'],
                                        font=('Segoe UI', 11),
                                        activebackground=self.colors['bg_card'])
        individual_check.pack(anchor=tk.W)
        
        # Action buttons
        self.create_action_buttons(sidebar_content)
    
    def create_action_buttons(self, parent):
        """Create prominent action buttons"""
        
        buttons_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Start button - prominent and inviting
        self.start_button = ttk.Button(buttons_frame,
                                      text="🚀 Start Scraping",
                                      style='Primary.TButton',
                                      command=self.start_scraping)
        self.start_button.pack(fill=tk.X, pady=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(buttons_frame,
                                     text="⏹️ Stop Scraping",
                                     style='Warning.TButton',
                                     command=self.stop_scraping,
                                     state='disabled')
        self.stop_button.pack(fill=tk.X, pady=(0, 10))
        
        # Export button
        self.export_button = ttk.Button(buttons_frame,
                                       text="💾 Export Results",
                                       style='Success.TButton',
                                       command=self.export_results)
        self.export_button.pack(fill=tk.X)
    
    def create_main_panel(self, parent):
        """Create main monitoring panel"""
        
        # Main panel container
        main_panel = ttk.Frame(parent, style='Card.TFrame')
        main_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_panel.columnconfigure(0, weight=1)
        main_panel.rowconfigure(1, weight=1)
        
        # Progress section
        self.create_progress_section(main_panel)
        
        # Results section
        self.create_results_section(main_panel)
    
    def create_progress_section(self, parent):
        """Create vibrant progress monitoring section"""
        
        progress_frame = ttk.LabelFrame(parent, text="📊 Scraping Progress", style='Card.TLabelframe')
        progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=20, pady=20)
        progress_frame.columnconfigure(1, weight=1)
        
        # Progress bar
        ttk.Label(progress_frame, text="Progress:", style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, padx=20, pady=15)
        
        self.progress_bar = ttk.Progressbar(progress_frame,
                                          variable=self.progress_var,
                                          maximum=100,
                                          length=400,
                                          style='Modern.Horizontal.TProgressbar')
        self.progress_bar.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 20), pady=15)
        
        # Progress text
        self.progress_text_var = tk.StringVar(value="0%")
        progress_text = ttk.Label(progress_frame, textvariable=self.progress_text_var, style='Success.TLabel')
        progress_text.grid(row=0, column=2, padx=(0, 20), pady=15)
        
        # Statistics
        stats_frame = tk.Frame(progress_frame, bg=self.colors['bg_card'])
        stats_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), padx=20, pady=(0, 15))
        
        # Create statistics labels
        self.stats_labels = {}
        stats_info = [
            ('pages_scraped', 'Pages Scraped', '0'),
            ('properties_found', 'Properties Found', '0'),
            ('duration', 'Duration', '0:00'),
            ('status', 'Status', 'Ready')
        ]
        
        for i, (key, label, default) in enumerate(stats_info):
            stat_frame = tk.Frame(stats_frame, bg=self.colors['bg_card'])
            stat_frame.grid(row=0, column=i, padx=15, pady=10)
            
            ttk.Label(stat_frame, text=label, style='Subtitle.TLabel').pack()
            self.stats_labels[key] = ttk.Label(stat_frame, text=default, style='Title.TLabel')
            self.stats_labels[key].pack()
    
    def create_results_section(self, parent):
        """Create results display section"""
        
        results_frame = ttk.LabelFrame(parent, text="📋 Scraping Log", style='Card.TLabelframe')
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=(0, 20))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Log text area with scrollbar
        log_frame = tk.Frame(results_frame, bg=self.colors['bg_card'])
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=15)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame,
                               font=('Consolas', 10),
                               bg=self.colors['bg_main'],
                               fg=self.colors['text_primary'],
                               relief='flat',
                               wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
    
    def create_footer(self, parent):
        """Create status footer"""
        
        footer_frame = tk.Frame(parent, bg=self.colors['bg_header'], height=50)
        footer_frame.pack(fill=tk.X)
        footer_frame.pack_propagate(False)
        
        # Status label
        status_label = ttk.Label(footer_frame, textvariable=self.status_var,
                               font=('Segoe UI', 11),
                               background=self.colors['bg_header'],
                               foreground=self.colors['text_white'])
        status_label.pack(side=tk.LEFT, padx=30, pady=15)
        
        # Version info
        version_label = ttk.Label(footer_frame, text="v2.0 Professional Edition",
                                font=('Segoe UI', 9),
                                background=self.colors['bg_header'],
                                foreground=self.colors['primary_light'])
        version_label.pack(side=tk.RIGHT, padx=30, pady=15)
    
    # Placeholder methods for functionality
    def start_scraping(self):
        """Start scraping process"""
        self.log_message("🚀 Starting scraping process...")
        self.status_var.set("Scraping in progress...")
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # Simulate progress
        self.simulate_progress()
    
    def stop_scraping(self):
        """Stop scraping process"""
        self.log_message("⏹️ Stopping scraping process...")
        self.status_var.set("Scraping stopped")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
    
    def export_results(self):
        """Export results"""
        self.log_message("💾 Exporting results...")
        messagebox.showinfo("Export", "Results exported successfully!")
    
    def simulate_progress(self):
        """Simulate scraping progress for demo"""
        def update_progress():
            for i in range(101):
                self.progress_var.set(i)
                self.progress_text_var.set(f"{i}%")
                self.stats_labels['pages_scraped'].config(text=str(i // 10))
                self.stats_labels['properties_found'].config(text=str(i * 30))
                self.root.update()
                self.root.after(50)
        
        threading.Thread(target=update_progress, daemon=True).start()
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
    
    def process_messages(self):
        """Process message queue"""
        # Placeholder for message processing
        self.root.after(100, self.process_messages)
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ModernMagicBricksGUI()
    app.run()
