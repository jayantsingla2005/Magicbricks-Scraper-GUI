#!/usr/bin/env python3
"""
GUI Styles Module
Handles all styling, theming, colors, fonts, and visual appearance.
Extracted from magicbricks_gui.py for better maintainability.
"""

from tkinter import ttk


class GUIStyles:
    """
    Manages all GUI styling including colors, fonts, and component styles
    """
    
    def __init__(self):
        """Initialize GUI styles"""
        self.style = ttk.Style()
        self.colors = {}
        self.fonts = {}
        
    def setup_modern_styles(self):
        """Setup modern, professional styling for the GUI with enhanced visual appeal"""
        
        # Try to use modern theme
        try:
            available_themes = self.style.theme_names()
            if 'vista' in available_themes:
                self.style.theme_use('vista')
            elif 'clam' in available_themes:
                self.style.theme_use('clam')
            else:
                self.style.theme_use('default')
        except:
            self.style.theme_use('default')

        # Enhanced modern color palette with gradients and depth
        self.colors = {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8fafc',
            'bg_accent': '#f1f5f9',
            'bg_card': '#ffffff',
            'text_primary': '#1e293b',
            'text_secondary': '#64748b',
            'text_muted': '#94a3b8',
            'primary': '#3b82f6',
            'primary_dark': '#2563eb',
            'primary_light': '#60a5fa',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#06b6d4',
            'border': '#e2e8f0',
            'border_light': '#f1f5f9',
            'shadow': '#0f172a15'
        }
        
        # Font configurations
        self.fonts = {
            'title': ('Segoe UI', 20, 'bold'),
            'subtitle': ('Segoe UI', 12),
            'heading': ('Segoe UI', 11, 'bold'),
            'body': ('Segoe UI', 10),
            'body_bold': ('Segoe UI', 10, 'bold'),
            'small': ('Segoe UI', 9),
            'icon': ('Segoe UI', 28),
            'monospace': ('Consolas', 9)
        }
        
        # Configure label styles
        self._configure_label_styles()
        
        # Configure button styles
        self._configure_button_styles()
        
        # Configure frame styles
        self._configure_frame_styles()
        
        # Configure entry and combobox styles
        self._configure_input_styles()
        
        # Configure progress bar styles
        self._configure_progress_styles()
    
    def _configure_label_styles(self):
        """Configure all label styles"""
        
        self.style.configure('Title.TLabel',
                           font=self.fonts['title'],
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'])

        self.style.configure('Subtitle.TLabel',
                           font=self.fonts['subtitle'],
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_secondary'])

        self.style.configure('Heading.TLabel',
                           font=self.fonts['heading'],
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'])

        self.style.configure('Info.TLabel',
                           font=self.fonts['body'],
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_secondary'])

        self.style.configure('Success.TLabel',
                           font=self.fonts['body_bold'],
                           background=self.colors['bg_primary'],
                           foreground=self.colors['success'])

        self.style.configure('Warning.TLabel',
                           font=self.fonts['body_bold'],
                           background=self.colors['bg_primary'],
                           foreground=self.colors['warning'])

        self.style.configure('Error.TLabel',
                           font=self.fonts['body_bold'],
                           background=self.colors['bg_primary'],
                           foreground=self.colors['danger'])

        self.style.configure('Muted.TLabel',
                           font=self.fonts['small'],
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_muted'])
    
    def _configure_button_styles(self):
        """Configure all button styles"""
        
        # Primary button
        self.style.configure('Primary.TButton',
                           font=self.fonts['heading'],
                           padding=(25, 12),
                           relief='flat')
        
        self.style.map('Primary.TButton',
                      background=[('active', self.colors['primary_dark']),
                                ('!active', self.colors['primary'])],
                      foreground=[('active', 'white'),
                                ('!active', 'white')])

        # Success button
        self.style.configure('Success.TButton',
                           font=self.fonts['body_bold'],
                           padding=(20, 10),
                           relief='flat')
        
        self.style.map('Success.TButton',
                      background=[('active', '#059669'),
                                ('!active', self.colors['success'])],
                      foreground=[('active', 'white'),
                                ('!active', 'white')])

        # Secondary button
        self.style.configure('Secondary.TButton',
                           font=self.fonts['body'],
                           padding=(15, 8),
                           relief='flat')
        
        self.style.map('Secondary.TButton',
                      background=[('active', self.colors['bg_accent']),
                                ('!active', self.colors['bg_secondary'])],
                      foreground=[('active', self.colors['text_primary']),
                                ('!active', self.colors['text_secondary'])])

        # Danger button
        self.style.configure('Danger.TButton',
                           font=self.fonts['body_bold'],
                           padding=(15, 8),
                           relief='flat')
        
        self.style.map('Danger.TButton',
                      background=[('active', '#dc2626'),
                                ('!active', self.colors['danger'])],
                      foreground=[('active', 'white'),
                                ('!active', 'white')])
    
    def _configure_frame_styles(self):
        """Configure all frame styles"""
        
        # Card frame
        self.style.configure('Card.TFrame',
                           background=self.colors['bg_card'],
                           relief='flat',
                           borderwidth=0)

        # Sidebar frame
        self.style.configure('Sidebar.TFrame',
                           background=self.colors['bg_secondary'],
                           relief='flat')
        
        # Modern labelframe
        self.style.configure('Modern.TLabelframe',
                           background=self.colors['bg_card'],
                           relief='flat',
                           borderwidth=1,
                           lightcolor=self.colors['border'],
                           darkcolor=self.colors['border'])
        
        self.style.configure('Modern.TLabelframe.Label',
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'],
                           font=self.fonts['heading'])
    
    def _configure_input_styles(self):
        """Configure entry and combobox styles"""
        
        # Entry style
        self.style.configure('Modern.TEntry',
                           fieldbackground=self.colors['bg_primary'],
                           borderwidth=2,
                           relief='flat',
                           insertcolor=self.colors['primary'])
        
        self.style.map('Modern.TEntry',
                      focuscolor=[('focus', self.colors['primary'])],
                      bordercolor=[('focus', self.colors['primary']),
                                 ('!focus', self.colors['border'])])

        # Combobox style
        self.style.configure('Modern.TCombobox',
                           fieldbackground=self.colors['bg_primary'],
                           borderwidth=2,
                           relief='flat')
        
        self.style.map('Modern.TCombobox',
                      focuscolor=[('focus', self.colors['primary'])],
                      bordercolor=[('focus', self.colors['primary']),
                                 ('!focus', self.colors['border'])])
    
    def _configure_progress_styles(self):
        """Configure progress bar styles"""
        
        self.style.configure('Modern.Horizontal.TProgressbar',
                           background=self.colors['primary'],
                           troughcolor=self.colors['bg_accent'],
                           borderwidth=0,
                           lightcolor=self.colors['primary'],
                           darkcolor=self.colors['primary'])
    
    def get_color(self, color_name: str) -> str:
        """
        Get color value by name
        
        Args:
            color_name: Name of the color
            
        Returns:
            Color hex value or default
        """
        return self.colors.get(color_name, '#000000')
    
    def get_font(self, font_name: str) -> tuple:
        """
        Get font configuration by name
        
        Args:
            font_name: Name of the font
            
        Returns:
            Font tuple (family, size, weight)
        """
        return self.fonts.get(font_name, ('Segoe UI', 10))
    
    def get_severity_config(self, severity: str) -> dict:
        """
        Get color and icon configuration for error severity
        
        Args:
            severity: Severity level (info, warning, error, critical)
            
        Returns:
            Dictionary with color and icon
        """
        severity_config = {
            'info': {'color': '#17a2b8', 'icon': 'ℹ️'},
            'warning': {'color': '#ffc107', 'icon': '⚠️'},
            'error': {'color': '#dc3545', 'icon': '❌'},
            'critical': {'color': '#6f42c1', 'icon': '🚨'}
        }
        return severity_config.get(severity.lower(), severity_config['info'])

