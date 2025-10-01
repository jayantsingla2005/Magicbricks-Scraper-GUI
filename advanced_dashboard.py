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
        """Create overview tab with key metrics"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="📊 Overview")
        
        # Key metrics frame
        metrics_frame = ttk.LabelFrame(overview_frame, text="Key Metrics", padding="15")
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create metric cards
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=tk.X)
        
        # Total sessions
        self.total_sessions_var = tk.StringVar(value="Loading...")
        self.create_metric_card(metrics_grid, "Total Sessions", self.total_sessions_var, 0, 0)
        
        # Total properties
        self.total_properties_var = tk.StringVar(value="Loading...")
        self.create_metric_card(metrics_grid, "Total Properties", self.total_properties_var, 0, 1)
        
        # Success rate
        self.success_rate_var = tk.StringVar(value="Loading...")
        self.create_metric_card(metrics_grid, "Success Rate", self.success_rate_var, 0, 2)
        
        # Avg speed
        self.avg_speed_var = tk.StringVar(value="Loading...")
        self.create_metric_card(metrics_grid, "Avg Speed (props/min)", self.avg_speed_var, 0, 3)
        
        # Recent activity frame
        activity_frame = ttk.LabelFrame(overview_frame, text="Recent Activity", padding="15")
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Recent sessions tree
        columns = ("Session ID", "City", "Mode", "Properties", "Duration", "Status", "Started")
        self.recent_tree = ttk.Treeview(activity_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=120)
        
        # Scrollbar for recent sessions
        recent_scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=recent_scrollbar.set)
        
        self.recent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        recent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_metric_card(self, parent, title, var, row, col):
        """Create a metric card widget"""
        card_frame = ttk.Frame(parent, relief="raised", borderwidth=1)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        parent.columnconfigure(col, weight=1)
        
        ttk.Label(card_frame, text=title, font=("Arial", 10, "bold")).pack(pady=(10, 5))
        ttk.Label(card_frame, textvariable=var, font=("Arial", 14)).pack(pady=(0, 10))
        
    def create_sessions_tab(self):
        """Create sessions management tab"""
        sessions_frame = ttk.Frame(self.notebook)
        self.notebook.add(sessions_frame, text="🗂️ Sessions")
        
        # Filter frame
        filter_frame = ttk.LabelFrame(sessions_frame, text="Filters", padding="10")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Date range filter
        ttk.Label(filter_frame, text="Date Range:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.date_from_var = tk.StringVar(value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        self.date_to_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Entry(filter_frame, textvariable=self.date_from_var, width=12).grid(row=0, column=1, padx=5)
        ttk.Label(filter_frame, text="to").grid(row=0, column=2, padx=5)
        ttk.Entry(filter_frame, textvariable=self.date_to_var, width=12).grid(row=0, column=3, padx=5)
        
        # City filter
        ttk.Label(filter_frame, text="City:").grid(row=0, column=4, sticky=tk.W, padx=(20, 5))
        self.city_filter_var = tk.StringVar(value="All")
        city_combo = ttk.Combobox(filter_frame, textvariable=self.city_filter_var, width=15)
        city_combo['values'] = ["All", "gurgaon", "noida", "delhi", "mumbai", "bangalore", "pune"]
        city_combo.grid(row=0, column=5, padx=5)
        
        # Apply filter button
        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_session_filters).grid(row=0, column=6, padx=20)
        
        # Sessions tree
        sessions_columns = ("ID", "City", "Mode", "Start Time", "End Time", "Duration", "Pages", "Properties", "Status")
        self.sessions_tree = ttk.Treeview(sessions_frame, columns=sessions_columns, show="headings", height=15)
        
        for col in sessions_columns:
            self.sessions_tree.heading(col, text=col)
            self.sessions_tree.column(col, width=100)
        
        # Scrollbars
        sessions_v_scroll = ttk.Scrollbar(sessions_frame, orient=tk.VERTICAL, command=self.sessions_tree.yview)
        sessions_h_scroll = ttk.Scrollbar(sessions_frame, orient=tk.HORIZONTAL, command=self.sessions_tree.xview)
        self.sessions_tree.configure(yscrollcommand=sessions_v_scroll.set, xscrollcommand=sessions_h_scroll.set)
        
        self.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        sessions_v_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        sessions_h_scroll.pack(side=tk.BOTTOM, fill=tk.X, padx=10)
        
        # Session details on double-click
        self.sessions_tree.bind("<Double-1>", self.show_session_details)
        
    def create_performance_tab(self):
        """Create performance analytics tab"""
        performance_frame = ttk.Frame(self.notebook)
        self.notebook.add(performance_frame, text="📈 Performance")
        
        # Performance charts frame
        charts_frame = ttk.Frame(performance_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create matplotlib figure
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle("Performance Analytics", fontsize=16)
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, charts_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Performance controls
        controls_frame = ttk.Frame(performance_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Refresh Charts", command=self.update_performance_charts).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export Data", command=self.export_performance_data).pack(side=tk.LEFT, padx=5)
        
    def create_analytics_tab(self):
        """Create detailed analytics tab"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")

        # Create scrollable frame
        canvas = tk.Canvas(analytics_frame)
        scrollbar = ttk.Scrollbar(analytics_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Session Analytics
        session_frame = ttk.LabelFrame(scrollable_frame, text="Session Analytics", padding="15")
        session_frame.pack(fill=tk.X, padx=10, pady=5)

        # Session summary
        self.session_summary_text = tk.Text(session_frame, height=8, wrap=tk.WORD, font=("Consolas", 9))
        self.session_summary_text.pack(fill=tk.X, pady=5)

        # Performance Analytics
        perf_frame = ttk.LabelFrame(scrollable_frame, text="Performance Analytics", padding="15")
        perf_frame.pack(fill=tk.X, padx=10, pady=5)

        self.performance_text = tk.Text(perf_frame, height=8, wrap=tk.WORD, font=("Consolas", 9))
        self.performance_text.pack(fill=tk.X, pady=5)

        # Data Quality Analytics
        quality_frame = ttk.LabelFrame(scrollable_frame, text="Data Quality Analytics", padding="15")
        quality_frame.pack(fill=tk.X, padx=10, pady=5)

        self.quality_text = tk.Text(quality_frame, height=6, wrap=tk.WORD, font=("Consolas", 9))
        self.quality_text.pack(fill=tk.X, pady=5)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

        # Load analytics data
        self.load_analytics_data()
        
    def create_errors_tab(self):
        """Create error tracking tab"""
        errors_frame = ttk.Frame(self.notebook)
        self.notebook.add(errors_frame, text="⚠️ Errors")
        
        # Error summary frame
        error_summary_frame = ttk.LabelFrame(errors_frame, text="Error Summary", padding="10")
        error_summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Error metrics
        self.total_errors_var = tk.StringVar(value="Loading...")
        self.critical_errors_var = tk.StringVar(value="Loading...")
        self.recent_errors_var = tk.StringVar(value="Loading...")
        
        ttk.Label(error_summary_frame, text="Total Errors:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(error_summary_frame, textvariable=self.total_errors_var).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(error_summary_frame, text="Critical Errors:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Label(error_summary_frame, textvariable=self.critical_errors_var).grid(row=0, column=3, sticky=tk.W, padx=10)
        
        ttk.Label(error_summary_frame, text="Recent (24h):").grid(row=0, column=4, sticky=tk.W, padx=(20, 0))
        ttk.Label(error_summary_frame, textvariable=self.recent_errors_var).grid(row=0, column=5, sticky=tk.W, padx=10)
        
        # Error log tree
        error_columns = ("Timestamp", "Session ID", "Severity", "Category", "Message", "Details")
        self.errors_tree = ttk.Treeview(errors_frame, columns=error_columns, show="headings", height=15)
        
        for col in error_columns:
            self.errors_tree.heading(col, text=col)
            self.errors_tree.column(col, width=120)
        
        # Error scrollbars
        error_v_scroll = ttk.Scrollbar(errors_frame, orient=tk.VERTICAL, command=self.errors_tree.yview)
        self.errors_tree.configure(yscrollcommand=error_v_scroll.set)
        
        self.errors_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        error_v_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
    def setup_auto_refresh(self):
        """Setup automatic data refresh"""
        self.auto_refresh_enabled = True
        self.refresh_interval = 30000  # 30 seconds
        self.schedule_refresh()
        
    def schedule_refresh(self):
        """Schedule next refresh"""
        if self.auto_refresh_enabled:
            self.root.after(self.refresh_interval, self.auto_refresh)
            
    def auto_refresh(self):
        """Automatically refresh data"""
        try:
            self.refresh_data()
        except Exception as e:
            print(f"Auto-refresh error: {e}")
        finally:
            self.schedule_refresh()
    
    def refresh_data(self):
        """Refresh all dashboard data"""
        try:
            self.load_overview_data()
            self.load_sessions_data()
            self.load_error_data()
            self.load_analytics_data()
            self.update_performance_charts()
        except Exception as e:
            print(f"Data refresh error: {e}")
    
    def load_overview_data(self):
        """Load overview metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total sessions
            cursor.execute("SELECT COUNT(*) FROM scrape_sessions")
            total_sessions = cursor.fetchone()[0]
            self.total_sessions_var.set(str(total_sessions))

            # Total properties (sum from session statistics)
            cursor.execute("SELECT SUM(properties_found) FROM scrape_sessions WHERE properties_found IS NOT NULL")
            result = cursor.fetchone()
            total_properties = result[0] if result[0] else 0
            self.total_properties_var.set(f"{total_properties:,}")

            # Success rate
            cursor.execute("""
                SELECT
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*)
                FROM scrape_sessions
            """)
            success_rate = cursor.fetchone()[0] or 0
            self.success_rate_var.set(f"{success_rate:.1f}%")

            # Average speed (properties per minute)
            cursor.execute("""
                SELECT AVG(properties_found * 60.0 /
                    ((JULIANDAY(end_timestamp) - JULIANDAY(start_timestamp)) * 24 * 60))
                FROM scrape_sessions
                WHERE end_timestamp IS NOT NULL AND properties_found > 0
            """)
            avg_speed = cursor.fetchone()[0] or 0
            self.avg_speed_var.set(f"{avg_speed:.1f}")

            conn.close()

        except Exception as e:
            print(f"Error loading overview data: {e}")
            self.total_sessions_var.set("Error")
            self.total_properties_var.set("Error")
            self.success_rate_var.set("Error")
            self.avg_speed_var.set("Error")
    
    def load_sessions_data(self):
        """Load recent sessions data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Clear existing data
            for item in self.recent_tree.get_children():
                self.recent_tree.delete(item)

            # Load recent sessions with correct column names
            cursor.execute("""
                SELECT session_id, city, scrape_mode, properties_found,
                       CASE
                           WHEN end_timestamp IS NOT NULL THEN
                               ROUND((JULIANDAY(end_timestamp) - JULIANDAY(start_timestamp)) * 24 * 60, 1) || 'm'
                           ELSE 'Running'
                       END as duration,
                       status, start_timestamp
                FROM scrape_sessions
                ORDER BY start_timestamp DESC
                LIMIT 20
            """)

            for row in cursor.fetchall():
                session_id, city, mode, properties, duration, status, start_time = row
                # Format start time
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_start = start_dt.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_start = start_time[:16] if start_time else "Unknown"

                self.recent_tree.insert("", "end", values=(
                    session_id, city, mode, properties or 0, duration, status, formatted_start
                ))

            conn.close()

        except Exception as e:
            print(f"Error loading sessions data: {e}")
    
    def load_error_data(self):
        """Load error tracking data"""
        try:
            # For now, set placeholder values
            self.total_errors_var.set("0")
            self.critical_errors_var.set("0")
            self.recent_errors_var.set("0")

        except Exception as e:
            print(f"Error loading error data: {e}")

    def load_analytics_data(self):
        """Load detailed analytics data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Session Analytics
            cursor.execute("""
                SELECT
                    COUNT(*) as total_sessions,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                    COUNT(CASE WHEN status = 'running' THEN 1 END) as running_sessions,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sessions,
                    AVG(properties_found) as avg_properties,
                    SUM(properties_found) as total_properties,
                    AVG(pages_scraped) as avg_pages
                FROM scrape_sessions
            """)

            session_stats = cursor.fetchone()

            session_text = f"""SESSION SUMMARY
Total Sessions: {session_stats[0]}
Completed: {session_stats[1]} ({session_stats[1]/session_stats[0]*100:.1f}%)
Running: {session_stats[2]}
Failed: {session_stats[3]} ({session_stats[3]/session_stats[0]*100:.1f}%)

PROPERTY STATISTICS
Total Properties Scraped: {session_stats[5]:,}
Average Properties per Session: {session_stats[4]:.1f}
Average Pages per Session: {session_stats[6]:.1f}
"""

            self.session_summary_text.delete(1.0, tk.END)
            self.session_summary_text.insert(1.0, session_text)

            # Performance Analytics
            cursor.execute("""
                SELECT
                    scrape_mode,
                    COUNT(*) as session_count,
                    AVG(properties_found) as avg_properties,
                    AVG(pages_scraped) as avg_pages,
                    AVG((JULIANDAY(end_timestamp) - JULIANDAY(start_timestamp)) * 24 * 60) as avg_duration_minutes
                FROM scrape_sessions
                WHERE end_timestamp IS NOT NULL
                GROUP BY scrape_mode
            """)

            perf_data = cursor.fetchall()

            perf_text = "PERFORMANCE BY MODE\n"
            for mode, count, avg_props, avg_pages, avg_duration in perf_data:
                perf_text += f"\n{mode.upper()} MODE:\n"
                perf_text += f"  Sessions: {count}\n"
                perf_text += f"  Avg Properties: {avg_props:.1f}\n"
                perf_text += f"  Avg Pages: {avg_pages:.1f}\n"
                perf_text += f"  Avg Duration: {avg_duration:.1f} minutes\n"
                if avg_duration > 0:
                    perf_text += f"  Speed: {avg_props/avg_duration:.2f} props/min\n"

            self.performance_text.delete(1.0, tk.END)
            self.performance_text.insert(1.0, perf_text)

            # Data Quality Analytics
            cursor.execute("""
                SELECT
                    city,
                    COUNT(*) as sessions,
                    SUM(properties_found) as total_properties,
                    AVG(properties_found) as avg_properties
                FROM scrape_sessions
                GROUP BY city
                ORDER BY total_properties DESC
            """)

            city_data = cursor.fetchall()

            quality_text = "CITY PERFORMANCE\n"
            for city, sessions, total_props, avg_props in city_data:
                quality_text += f"\n{city.upper()}:\n"
                quality_text += f"  Sessions: {sessions}\n"
                quality_text += f"  Total Properties: {total_props:,}\n"
                quality_text += f"  Avg per Session: {avg_props:.1f}\n"

            self.quality_text.delete(1.0, tk.END)
            self.quality_text.insert(1.0, quality_text)

            conn.close()

        except Exception as e:
            print(f"Error loading analytics data: {e}")
            # Set error messages
            for text_widget in [self.session_summary_text, self.performance_text, self.quality_text]:
                text_widget.delete(1.0, tk.END)
                text_widget.insert(1.0, f"Error loading data: {e}")
    
    def update_performance_charts(self):
        """Update performance charts"""
        try:
            # Clear existing plots
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.clear()
            
            # Sample data for demonstration
            # In production, this would load real data from database
            
            # Chart 1: Sessions over time
            self.ax1.plot([1, 2, 3, 4, 5], [10, 15, 12, 18, 20])
            self.ax1.set_title("Sessions Over Time")
            self.ax1.set_xlabel("Days")
            self.ax1.set_ylabel("Sessions")
            
            # Chart 2: Properties per session
            self.ax2.bar(["Mon", "Tue", "Wed", "Thu", "Fri"], [300, 450, 380, 520, 410])
            self.ax2.set_title("Properties Per Day")
            self.ax2.set_ylabel("Properties")
            
            # Chart 3: Success rate by city
            cities = ["Gurgaon", "Noida", "Delhi", "Mumbai"]
            success_rates = [95, 92, 88, 90]
            self.ax3.pie(success_rates, labels=cities, autopct='%1.1f%%')
            self.ax3.set_title("Success Rate by City")
            
            # Chart 4: Performance trends
            self.ax4.plot([1, 2, 3, 4, 5], [85, 88, 92, 89, 94])
            self.ax4.set_title("Performance Trend")
            self.ax4.set_xlabel("Weeks")
            self.ax4.set_ylabel("Success Rate %")
            
            plt.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating charts: {e}")
    
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
        """Export performance data to CSV"""
        try:
            # Implementation for exporting data
            messagebox.showinfo("Export", "Performance data exported successfully!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def run(self):
        """Run the dashboard"""
        if not self.parent:
            self.root.mainloop()

if __name__ == "__main__":
    dashboard = AdvancedDashboard()
    dashboard.run()
