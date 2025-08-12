#!/usr/bin/env python3
"""
Data Visualization Component - Charts and Analytics for Non-Technical Users
Provides intuitive visual insights into scraped property data
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class DataVisualizationPanel:
    """
    Interactive data visualization panel for property analytics
    Designed for non-technical users to understand data insights
    """
    
    def __init__(self, parent, style_manager):
        """
        Initialize data visualization panel
        
        Args:
            parent: Parent widget
            style_manager: StyleManager instance
        """
        
        self.parent = parent
        self.style_manager = style_manager
        
        # Sample data for demonstration
        self.sample_data = self.generate_sample_data()
        
        # Create the panel
        self.create_panel()
    
    def create_panel(self):
        """Create the data visualization panel"""
        
        # Main container
        self.frame = ttk.LabelFrame(self.parent, text="📊 Data Analytics Dashboard", style='Card.TLabelframe')
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create notebook for different chart types
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Create different visualization tabs
        self.create_overview_tab()
        self.create_price_analysis_tab()
        self.create_location_analysis_tab()
        self.create_trends_tab()
    
    def create_overview_tab(self):
        """Create overview dashboard tab"""
        
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="📈 Overview")
        
        # Configure grid
        overview_frame.columnconfigure(0, weight=1)
        overview_frame.columnconfigure(1, weight=1)
        overview_frame.rowconfigure(0, weight=1)
        overview_frame.rowconfigure(1, weight=1)
        
        # Key metrics cards
        self.create_metrics_cards(overview_frame)
        
        # Property type distribution (pie chart)
        self.create_property_type_chart(overview_frame)
        
        # Price range distribution (bar chart)
        self.create_price_range_chart(overview_frame)
        
        # Recent activity timeline
        self.create_activity_timeline(overview_frame)
    
    def create_price_analysis_tab(self):
        """Create price analysis tab"""
        
        price_frame = ttk.Frame(self.notebook)
        self.notebook.add(price_frame, text="💰 Price Analysis")
        
        # Price distribution histogram
        self.create_price_histogram(price_frame)
        
        # Price vs Area scatter plot
        self.create_price_area_scatter(price_frame)
    
    def create_location_analysis_tab(self):
        """Create location analysis tab"""
        
        location_frame = ttk.Frame(self.notebook)
        self.notebook.add(location_frame, text="📍 Location Analysis")
        
        # Top localities by count
        self.create_locality_chart(location_frame)
        
        # Average price by locality
        self.create_locality_price_chart(location_frame)
    
    def create_trends_tab(self):
        """Create trends analysis tab"""
        
        trends_frame = ttk.Frame(self.notebook)
        self.notebook.add(trends_frame, text="📈 Trends")
        
        # Scraping progress over time
        self.create_scraping_progress_chart(trends_frame)
        
        # Properties found per day
        self.create_daily_properties_chart(trends_frame)
    
    def create_metrics_cards(self, parent):
        """Create key metrics cards"""
        
        metrics_frame = tk.Frame(parent, bg=self.style_manager.get_color('bg_card'))
        metrics_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        # Sample metrics
        metrics = [
            ("Total Properties", "1,247", "🏠", self.style_manager.get_color('primary')),
            ("Average Price", "₹85.6 Lakh", "💰", self.style_manager.get_color('secondary')),
            ("Price Range", "₹15L - ₹5.2Cr", "📊", self.style_manager.get_color('accent')),
            ("Top Locality", "DLF Phase 2", "📍", self.style_manager.get_color('info'))
        ]
        
        for i, (title, value, icon, color) in enumerate(metrics):
            card = tk.Frame(metrics_frame, bg=color, relief='flat', bd=0)
            card.grid(row=0, column=i, padx=10, pady=10, sticky=(tk.W, tk.E))
            metrics_frame.columnconfigure(i, weight=1)
            
            # Icon and title
            header_frame = tk.Frame(card, bg=color)
            header_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
            
            icon_label = tk.Label(header_frame, text=icon, bg=color, fg='white', font=('Segoe UI', 16))
            icon_label.pack(side=tk.LEFT)
            
            title_label = tk.Label(header_frame, text=title, bg=color, fg='white', 
                                 font=('Segoe UI', 10, 'bold'))
            title_label.pack(side=tk.RIGHT)
            
            # Value
            value_label = tk.Label(card, text=value, bg=color, fg='white',
                                 font=('Segoe UI', 14, 'bold'))
            value_label.pack(padx=15, pady=(0, 10))
    
    def create_property_type_chart(self, parent):
        """Create property type distribution pie chart"""
        
        chart_frame = tk.Frame(parent, bg=self.style_manager.get_color('bg_card'))
        chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Create matplotlib figure
        fig = Figure(figsize=(6, 4), dpi=100, facecolor=self.style_manager.get_color('bg_card'))
        ax = fig.add_subplot(111)
        
        # Sample data
        property_types = ['Apartment', 'House', 'Plot', 'Villa', 'Studio']
        counts = [650, 320, 150, 85, 42]
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(counts, labels=property_types, colors=colors, 
                                         autopct='%1.1f%%', startangle=90)
        
        # Styling
        ax.set_title('Property Type Distribution', fontsize=14, fontweight='bold', pad=20)
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_price_range_chart(self, parent):
        """Create price range distribution bar chart"""
        
        chart_frame = tk.Frame(parent, bg=self.style_manager.get_color('bg_card'))
        chart_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Create matplotlib figure
        fig = Figure(figsize=(6, 4), dpi=100, facecolor=self.style_manager.get_color('bg_card'))
        ax = fig.add_subplot(111)
        
        # Sample data
        price_ranges = ['<₹50L', '₹50L-₹1Cr', '₹1Cr-₹2Cr', '₹2Cr-₹5Cr', '>₹5Cr']
        counts = [245, 487, 312, 156, 47]
        
        # Create bar chart
        bars = ax.bar(price_ranges, counts, color=self.style_manager.get_color('secondary'), alpha=0.8)
        
        # Styling
        ax.set_title('Price Range Distribution', fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Number of Properties')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_activity_timeline(self, parent):
        """Create recent activity timeline"""
        
        timeline_frame = tk.Frame(parent, bg=self.style_manager.get_color('bg_card'))
        timeline_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        
        # Timeline header
        header_label = tk.Label(timeline_frame, text="📅 Recent Scraping Activity", 
                               bg=self.style_manager.get_color('bg_card'),
                               fg=self.style_manager.get_color('text_primary'),
                               font=('Segoe UI', 12, 'bold'))
        header_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Timeline items
        activities = [
            ("2 hours ago", "Completed scraping 150 properties from Gurgaon", "✅"),
            ("5 hours ago", "Started individual property detail extraction", "🏠"),
            ("1 day ago", "Scraped 300 properties from Mumbai", "✅"),
            ("2 days ago", "Updated database schema for better performance", "🔧")
        ]
        
        for time_str, activity, icon in activities:
            item_frame = tk.Frame(timeline_frame, bg=self.style_manager.get_color('bg_main'))
            item_frame.pack(fill=tk.X, padx=15, pady=2)
            
            # Icon
            icon_label = tk.Label(item_frame, text=icon, bg=self.style_manager.get_color('bg_main'),
                                font=('Segoe UI', 12))
            icon_label.pack(side=tk.LEFT, padx=(10, 15), pady=8)
            
            # Content
            content_frame = tk.Frame(item_frame, bg=self.style_manager.get_color('bg_main'))
            content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8)
            
            activity_label = tk.Label(content_frame, text=activity, 
                                    bg=self.style_manager.get_color('bg_main'),
                                    fg=self.style_manager.get_color('text_primary'),
                                    font=('Segoe UI', 10))
            activity_label.pack(anchor=tk.W)
            
            time_label = tk.Label(content_frame, text=time_str,
                                bg=self.style_manager.get_color('bg_main'),
                                fg=self.style_manager.get_color('text_secondary'),
                                font=('Segoe UI', 9))
            time_label.pack(anchor=tk.W)
    
    def create_price_histogram(self, parent):
        """Create price distribution histogram"""
        
        chart_frame = tk.Frame(parent, bg=self.style_manager.get_color('bg_card'))
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6), dpi=100, facecolor=self.style_manager.get_color('bg_card'))
        ax = fig.add_subplot(111)
        
        # Generate sample price data
        np.random.seed(42)
        prices = np.random.lognormal(mean=17.5, sigma=0.8, size=1000) / 100000  # Convert to lakhs
        
        # Create histogram
        n, bins, patches = ax.hist(prices, bins=30, color=self.style_manager.get_color('primary'), 
                                  alpha=0.7, edgecolor='white')
        
        # Styling
        ax.set_title('Property Price Distribution', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Price (₹ Lakhs)')
        ax.set_ylabel('Number of Properties')
        ax.grid(True, alpha=0.3)
        
        # Add statistics text
        mean_price = np.mean(prices)
        median_price = np.median(prices)
        stats_text = f'Mean: ₹{mean_price:.1f}L\nMedian: ₹{median_price:.1f}L'
        ax.text(0.7, 0.8, stats_text, transform=ax.transAxes, fontsize=12,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_price_area_scatter(self, parent):
        """Create price vs area scatter plot"""
        
        chart_frame = tk.Frame(parent, bg=self.style_manager.get_color('bg_card'))
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6), dpi=100, facecolor=self.style_manager.get_color('bg_card'))
        ax = fig.add_subplot(111)
        
        # Generate sample data
        np.random.seed(42)
        areas = np.random.normal(1200, 400, 500)  # Square feet
        areas = np.clip(areas, 500, 3000)  # Reasonable range
        
        # Price roughly correlates with area
        prices = (areas * 0.08 + np.random.normal(0, 20, 500)) / 10  # Convert to lakhs
        prices = np.clip(prices, 20, 500)  # Reasonable range
        
        # Create scatter plot
        scatter = ax.scatter(areas, prices, c=prices, cmap='viridis', alpha=0.6, s=50)
        
        # Add trend line
        z = np.polyfit(areas, prices, 1)
        p = np.poly1d(z)
        ax.plot(areas, p(areas), "r--", alpha=0.8, linewidth=2)
        
        # Styling
        ax.set_title('Property Price vs Area Analysis', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Area (Square Feet)')
        ax.set_ylabel('Price (₹ Lakhs)')
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label('Price (₹ Lakhs)')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_locality_chart(self, parent):
        """Create top localities chart"""
        
        chart_frame = tk.Frame(parent, bg=self.style_manager.get_color('bg_card'))
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6), dpi=100, facecolor=self.style_manager.get_color('bg_card'))
        ax = fig.add_subplot(111)
        
        # Sample data
        localities = ['DLF Phase 2', 'Sector 57', 'Golf Course Road', 'Sohna Road', 
                     'MG Road', 'Cyber City', 'New Gurgaon', 'Old Gurgaon']
        counts = [156, 134, 98, 87, 76, 65, 54, 43]
        
        # Create horizontal bar chart
        bars = ax.barh(localities, counts, color=self.style_manager.get_color('accent'), alpha=0.8)
        
        # Styling
        ax.set_title('Top Localities by Property Count', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Number of Properties')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2,
                   f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_locality_price_chart(self, parent):
        """Create average price by locality chart"""
        
        chart_frame = tk.Frame(parent, bg=self.style_manager.get_color('bg_card'))
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6), dpi=100, facecolor=self.style_manager.get_color('bg_card'))
        ax = fig.add_subplot(111)
        
        # Sample data
        localities = ['Golf Course Road', 'DLF Phase 2', 'Cyber City', 'Sector 57', 
                     'MG Road', 'Sohna Road', 'New Gurgaon', 'Old Gurgaon']
        avg_prices = [145, 125, 110, 95, 85, 75, 65, 55]  # In lakhs
        
        # Create bar chart with gradient colors
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(localities)))
        bars = ax.bar(localities, avg_prices, color=colors, alpha=0.8)
        
        # Styling
        ax.set_title('Average Property Price by Locality', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Average Price (₹ Lakhs)')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'₹{int(height)}L', ha='center', va='bottom', fontweight='bold')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_scraping_progress_chart(self, parent):
        """Create scraping progress over time chart"""
        
        chart_frame = tk.Frame(parent, bg=self.style_manager.get_color('bg_card'))
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6), dpi=100, facecolor=self.style_manager.get_color('bg_card'))
        ax = fig.add_subplot(111)
        
        # Generate sample time series data
        dates = pd.date_range(start='2025-08-01', end='2025-08-12', freq='D')
        cumulative_properties = np.cumsum(np.random.randint(50, 200, len(dates)))
        
        # Create line chart
        ax.plot(dates, cumulative_properties, marker='o', linewidth=3, 
               color=self.style_manager.get_color('primary'), markersize=6)
        
        # Fill area under curve
        ax.fill_between(dates, cumulative_properties, alpha=0.3, 
                       color=self.style_manager.get_color('primary'))
        
        # Styling
        ax.set_title('Cumulative Properties Scraped Over Time', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date')
        ax.set_ylabel('Total Properties Scraped')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        fig.autofmt_xdate()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_daily_properties_chart(self, parent):
        """Create daily properties found chart"""
        
        chart_frame = tk.Frame(parent, bg=self.style_manager.get_color('bg_card'))
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Create matplotlib figure
        fig = Figure(figsize=(10, 6), dpi=100, facecolor=self.style_manager.get_color('bg_card'))
        ax = fig.add_subplot(111)
        
        # Generate sample daily data
        dates = pd.date_range(start='2025-08-01', end='2025-08-12', freq='D')
        daily_properties = np.random.randint(80, 250, len(dates))
        
        # Create bar chart
        bars = ax.bar(dates, daily_properties, color=self.style_manager.get_color('secondary'), 
                     alpha=0.8, width=0.8)
        
        # Add trend line
        x_numeric = np.arange(len(dates))
        z = np.polyfit(x_numeric, daily_properties, 1)
        p = np.poly1d(z)
        ax.plot(dates, p(x_numeric), "r--", alpha=0.8, linewidth=2, label='Trend')
        
        # Styling
        ax.set_title('Daily Properties Found', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date')
        ax.set_ylabel('Properties Found')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format x-axis
        fig.autofmt_xdate()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def generate_sample_data(self):
        """Generate sample data for demonstration"""
        
        # This would be replaced with actual scraped data
        return {
            'total_properties': 1247,
            'average_price': 85.6,
            'price_range': (15, 520),
            'top_locality': 'DLF Phase 2'
        }
    
    def update_data(self, new_data: Dict[str, Any]):
        """Update visualizations with new data"""
        
        # This method would refresh all charts with new data
        # For now, it's a placeholder for future implementation
        pass
