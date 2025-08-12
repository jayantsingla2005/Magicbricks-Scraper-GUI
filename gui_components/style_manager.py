#!/usr/bin/env python3
"""
Style Manager - Centralized styling for the MagicBricks GUI
Separates all styling logic from the main GUI code
"""

from tkinter import ttk


class StyleManager:
    """
    Manages all GUI styling in a centralized, maintainable way
    """
    
    def __init__(self):
        """Initialize the style manager"""
        
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
        
        # Typography settings
        self.fonts = {
            'header': ('Segoe UI', 24, 'bold'),
            'subheader': ('Segoe UI', 14),
            'title': ('Segoe UI', 16, 'bold'),
            'subtitle': ('Segoe UI', 12),
            'body': ('Segoe UI', 11),
            'small': ('Segoe UI', 10),
            'tiny': ('Segoe UI', 9),
            'code': ('Consolas', 10),
            'button': ('Segoe UI', 11, 'bold'),
            'button_large': ('Segoe UI', 12, 'bold')
        }
        
        self.style = None
    
    def setup_styles(self, root):
        """Setup all styles for the application"""
        
        self.style = ttk.Style()
        
        # Use modern theme as base
        try:
            self.style.theme_use('clam')
        except:
            self.style.theme_use('default')
        
        # Configure root window
        root.configure(bg=self.colors['bg_main'])
        
        # Setup all style categories
        self._setup_text_styles()
        self._setup_button_styles()
        self._setup_frame_styles()
        self._setup_input_styles()
        self._setup_progress_styles()
        self._setup_tree_styles()
    
    def _setup_text_styles(self):
        """Setup text and label styles"""
        
        # Header styles
        self.style.configure('Header.TLabel',
                           font=self.fonts['header'],
                           background=self.colors['bg_header'],
                           foreground=self.colors['text_white'],
                           padding=(20, 15))
        
        self.style.configure('Subheader.TLabel',
                           font=self.fonts['subheader'],
                           background=self.colors['bg_header'],
                           foreground=self.colors['primary_light'],
                           padding=(20, 5))
        
        # Content text styles
        self.style.configure('Title.TLabel',
                           font=self.fonts['title'],
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'])
        
        self.style.configure('Subtitle.TLabel',
                           font=self.fonts['subtitle'],
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_secondary'])
        
        self.style.configure('Body.TLabel',
                           font=self.fonts['body'],
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'])
        
        self.style.configure('Small.TLabel',
                           font=self.fonts['small'],
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_secondary'])
        
        # Status text styles
        self.style.configure('Success.TLabel',
                           font=self.fonts['body'],
                           background=self.colors['bg_card'],
                           foreground=self.colors['success'])
        
        self.style.configure('Warning.TLabel',
                           font=self.fonts['body'],
                           background=self.colors['bg_card'],
                           foreground=self.colors['warning'])
        
        self.style.configure('Error.TLabel',
                           font=self.fonts['body'],
                           background=self.colors['bg_card'],
                           foreground=self.colors['error'])
        
        self.style.configure('Info.TLabel',
                           font=self.fonts['body'],
                           background=self.colors['bg_card'],
                           foreground=self.colors['info'])
    
    def _setup_button_styles(self):
        """Setup button styles"""
        
        # Primary button - main actions
        self.style.configure('Primary.TButton',
                           font=self.fonts['button_large'],
                           padding=(30, 15),
                           relief='flat',
                           borderwidth=0)
        
        self.style.map('Primary.TButton',
                      background=[('active', self.colors['primary_dark']),
                                ('!active', self.colors['primary'])],
                      foreground=[('active', self.colors['text_white']),
                                ('!active', self.colors['text_white'])])
        
        # Success button - positive actions
        self.style.configure('Success.TButton',
                           font=self.fonts['button'],
                           padding=(25, 12),
                           relief='flat')
        
        self.style.map('Success.TButton',
                      background=[('active', '#059669'),
                                ('!active', self.colors['secondary'])],
                      foreground=[('active', self.colors['text_white']),
                                ('!active', self.colors['text_white'])])
        
        # Warning button - caution actions
        self.style.configure('Warning.TButton',
                           font=self.fonts['button'],
                           padding=(25, 12),
                           relief='flat')
        
        self.style.map('Warning.TButton',
                      background=[('active', '#d97706'),
                                ('!active', self.colors['accent'])],
                      foreground=[('active', self.colors['text_white']),
                                ('!active', self.colors['text_white'])])
        
        # Danger button - destructive actions
        self.style.configure('Danger.TButton',
                           font=self.fonts['button'],
                           padding=(20, 10),
                           relief='flat')
        
        self.style.map('Danger.TButton',
                      background=[('active', '#dc2626'),
                                ('!active', self.colors['error'])],
                      foreground=[('active', self.colors['text_white']),
                                ('!active', self.colors['text_white'])])
        
        # Secondary button - less important actions
        self.style.configure('Secondary.TButton',
                           font=self.fonts['button'],
                           padding=(20, 10),
                           relief='flat')
        
        self.style.map('Secondary.TButton',
                      background=[('active', self.colors['border_dark']),
                                ('!active', self.colors['border'])],
                      foreground=[('active', self.colors['text_primary']),
                                ('!active', self.colors['text_secondary'])])
    
    def _setup_frame_styles(self):
        """Setup frame and container styles"""
        
        # Card frame - elevated content
        self.style.configure('Card.TFrame',
                           background=self.colors['bg_card'],
                           relief='flat',
                           borderwidth=0)
        
        # Card with border
        self.style.configure('Card.TLabelframe',
                           background=self.colors['bg_card'],
                           relief='flat',
                           borderwidth=2,
                           lightcolor=self.colors['border'],
                           darkcolor=self.colors['border'])
        
        # Sidebar frame
        self.style.configure('Sidebar.TFrame',
                           background=self.colors['bg_sidebar'],
                           relief='flat')
        
        # Header frame
        self.style.configure('Header.TFrame',
                           background=self.colors['bg_header'],
                           relief='flat')
    
    def _setup_input_styles(self):
        """Setup input field styles"""
        
        # Entry fields
        self.style.configure('Modern.TEntry',
                           font=self.fonts['body'],
                           relief='flat',
                           borderwidth=1,
                           lightcolor=self.colors['border'],
                           darkcolor=self.colors['border'])
        
        # Combobox
        self.style.configure('Modern.TCombobox',
                           font=self.fonts['body'],
                           relief='flat',
                           borderwidth=1)
    
    def _setup_progress_styles(self):
        """Setup progress bar styles"""
        
        self.style.configure('Modern.Horizontal.TProgressbar',
                           background=self.colors['primary'],
                           troughcolor=self.colors['bg_main'],
                           borderwidth=0,
                           lightcolor=self.colors['primary'],
                           darkcolor=self.colors['primary'])
        
        self.style.configure('Success.Horizontal.TProgressbar',
                           background=self.colors['secondary'],
                           troughcolor=self.colors['bg_main'],
                           borderwidth=0)
    
    def _setup_tree_styles(self):
        """Setup treeview/table styles"""
        
        self.style.configure('Modern.Treeview',
                           font=self.fonts['body'],
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'],
                           fieldbackground=self.colors['bg_card'],
                           borderwidth=0)
        
        self.style.configure('Modern.Treeview.Heading',
                           font=self.fonts['subtitle'],
                           background=self.colors['bg_main'],
                           foreground=self.colors['text_primary'],
                           relief='flat')
    
    def get_color(self, color_name: str) -> str:
        """Get a color value by name"""
        return self.colors.get(color_name, '#000000')
    
    def get_font(self, font_name: str) -> tuple:
        """Get a font configuration by name"""
        return self.fonts.get(font_name, ('Segoe UI', 11))
    
    def create_gradient_effect(self, widget, start_color: str, end_color: str):
        """Create a gradient effect (placeholder for future implementation)"""
        # This would require custom drawing or using Canvas
        pass
