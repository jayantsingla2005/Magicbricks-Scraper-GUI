"""
Overview tab builder extracted from advanced_dashboard.py
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta


def create_metric_card(parent, title, var, row, col):
    card_frame = ttk.Frame(parent, relief="raised", borderwidth=1)
    card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
    parent.columnconfigure(col, weight=1)
    ttk.Label(card_frame, text=title, font=("Arial", 10, "bold")).pack(pady=(10, 5))
    ttk.Label(card_frame, textvariable=var, font=("Arial", 14)).pack(pady=(0, 10))


def build_overview_tab(d):
    """Build the Overview tab on the given dashboard instance d"""
    overview_frame = ttk.Frame(d.notebook)
    d.notebook.add(overview_frame, text="📊 Overview")

    metrics_frame = ttk.LabelFrame(overview_frame, text="Key Metrics", padding="15")
    metrics_frame.pack(fill=tk.X, padx=10, pady=5)

    metrics_grid = ttk.Frame(metrics_frame)
    metrics_grid.pack(fill=tk.X)

    d.total_sessions_var = tk.StringVar(value="Loading...")
    create_metric_card(metrics_grid, "Total Sessions", d.total_sessions_var, 0, 0)

    d.total_properties_var = tk.StringVar(value="Loading...")
    create_metric_card(metrics_grid, "Total Properties", d.total_properties_var, 0, 1)

    d.success_rate_var = tk.StringVar(value="Loading...")
    create_metric_card(metrics_grid, "Success Rate", d.success_rate_var, 0, 2)

    d.avg_speed_var = tk.StringVar(value="Loading...")
    create_metric_card(metrics_grid, "Avg Speed (props/min)", d.avg_speed_var, 0, 3)

    activity_frame = ttk.LabelFrame(overview_frame, text="Recent Activity", padding="15")
    activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("Session ID", "City", "Mode", "Properties", "Duration", "Status", "Started")
    d.recent_tree = ttk.Treeview(activity_frame, columns=columns, show="headings", height=10)
    for col in columns:
        d.recent_tree.heading(col, text=col)
        d.recent_tree.column(col, width=120)

    recent_scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=d.recent_tree.yview)
    d.recent_tree.configure(yscrollcommand=recent_scrollbar.set)
    d.recent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    recent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

