#!/usr/bin/env python3
"""
Advanced Dashboard for MagicBricks Scraper
Production-ready dashboard with complete scraping history, session summaries,
performance metrics, error tracking, and detailed analytics.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import threading
import time

import dashboard_overview_tab
import dashboard_sessions_tab
import dashboard_performance_tab
import dashboard_analytics_tab
import dashboard_errors_tab
import dashboard_refresh
import dashboard_data_overview

class AdvancedDashboard:
    """Advanced dashboard for production scraping management"""

    def __init__(self, parent=None):
        self.parent = parent
        self.db_path = "magicbricks_enhanced.db"
        self.setup_dashboard()
        self.refresh_data()

    def setup_dashboard(self):
        """Setup the advanced dashboard interface"""
        if self.parent:
            self.root = tk.Toplevel(self.parent)
        else:
            self.root = tk.Tk()

        self.root.title("MagicBricks Scraper - Advanced Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        # Create main container with notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_overview_tab()
        self.create_sessions_tab()
        self.create_performance_tab()
        self.create_analytics_tab()
        self.create_errors_tab()

        # Auto-refresh timer
        self.setup_auto_refresh()

    def create_overview_tab(self):
        """Create overview tab with key metrics (delegated)"""
        return dashboard_overview_tab.build_overview_tab(self)

    
    def create_sessions_tab(self):
        """Create sessions management tab (delegated)"""
        return dashboard_sessions_tab.build_sessions_tab(self)

    def create_performance_tab(self):
        """Create performance analytics tab (delegated)"""
        return dashboard_performance_tab.build_performance_tab(self)

    def create_analytics_tab(self):
        """Create detailed analytics tab (delegated)"""
        return dashboard_analytics_tab.build_analytics_tab(self)

    def create_errors_tab(self):
        """Create error tracking tab (delegated)"""
        return dashboard_errors_tab.build_errors_tab(self)

    def setup_auto_refresh(self):
        """Setup automatic data refresh (delegated)"""
        return dashboard_refresh.setup_auto_refresh(self)

    def schedule_refresh(self):
        """Schedule next refresh (delegated)"""
        return dashboard_refresh.schedule_refresh(self)

    def auto_refresh(self):
        """Automatically refresh data (delegated)"""
        return dashboard_refresh.auto_refresh(self)

    def refresh_data(self):
        """Refresh all dashboard data (delegated)"""
        return dashboard_refresh.refresh_data(self)

    def load_overview_data(self):
        """Load overview metrics (delegated)"""
        return dashboard_data_overview.load_overview_data(self)

    def load_sessions_data(self):
        """Load recent sessions data (delegated)"""
        return dashboard_data_overview.load_sessions_data(self)

    def load_error_data(self):
        """Load error tracking data (delegated)"""
        return dashboard_errors_tab.load_error_data(self)

    def load_analytics_data(self):
        """Load detailed analytics data (delegated)"""
        return dashboard_analytics_tab.load_analytics_data(self)

    def update_performance_charts(self):
        """Update performance charts (delegated)"""
        return dashboard_performance_tab.update_performance_charts(self)

    def apply_session_filters(self):
        """Apply filters to sessions view"""
        # Implementation for filtering sessions
        self.load_sessions_data()

    def show_session_details(self, event):
        """Show detailed session information"""
        selection = self.sessions_tree.selection()
        if selection:
            item = self.sessions_tree.item(selection[0])
            session_id = item['values'][0]

            # Create session details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Session {session_id} Details")
            details_window.geometry("600x400")

            ttk.Label(details_window, text=f"Session {session_id} Details",
                     font=("Arial", 14, "bold")).pack(pady=10)

            # Add session details here
            ttk.Label(details_window, text="Detailed session information would be displayed here").pack()

    def export_performance_data(self):
        """Export performance data to CSV (delegated)"""
        return dashboard_performance_tab.export_performance_data(self)

    def run(self):
        """Run the dashboard"""
        if not self.parent:
            self.root.mainloop()

if __name__ == "__main__":
    dashboard = AdvancedDashboard()
    dashboard.run()
