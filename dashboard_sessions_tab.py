"""
Sessions tab builder extracted from advanced_dashboard.py
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import sqlite3


def build_sessions_tab(d):
    sessions_frame = ttk.Frame(d.notebook)
    d.notebook.add(sessions_frame, text=" Sessions")

    filter_frame = ttk.LabelFrame(sessions_frame, text="Filters", padding="10")
    filter_frame.pack(fill=tk.X, padx=10, pady=5)

    ttk.Label(filter_frame, text="Date Range:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
    d.date_from_var = tk.StringVar(value=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
    d.date_to_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

    ttk.Entry(filter_frame, textvariable=d.date_from_var, width=12).grid(row=0, column=1, padx=5)
    ttk.Label(filter_frame, text="to").grid(row=0, column=2, padx=5)
    ttk.Entry(filter_frame, textvariable=d.date_to_var, width=12).grid(row=0, column=3, padx=5)

    ttk.Label(filter_frame, text="City:").grid(row=0, column=4, sticky=tk.W, padx=(20, 5))
    d.city_filter_var = tk.StringVar(value="All")
    city_combo = ttk.Combobox(filter_frame, textvariable=d.city_filter_var, width=15)
    city_combo['values'] = ["All", "gurgaon", "noida", "delhi", "mumbai", "bangalore", "pune"]
    city_combo.grid(row=0, column=5, padx=5)

    ttk.Button(filter_frame, text="Apply Filters", command=d.apply_session_filters).grid(row=0, column=6, padx=20)

    sessions_columns = ("ID", "City", "Mode", "Start Time", "End Time", "Duration", "Pages", "Properties", "Status")
    d.sessions_tree = ttk.Treeview(sessions_frame, columns=sessions_columns, show="headings", height=15)
    for col in sessions_columns:
        d.sessions_tree.heading(col, text=col)
        d.sessions_tree.column(col, width=100)

    sessions_v_scroll = ttk.Scrollbar(sessions_frame, orient=tk.VERTICAL, command=d.sessions_tree.yview)
    sessions_h_scroll = ttk.Scrollbar(sessions_frame, orient=tk.HORIZONTAL, command=d.sessions_tree.xview)
    d.sessions_tree.configure(yscrollcommand=sessions_v_scroll.set, xscrollcommand=sessions_h_scroll.set)

    d.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
    sessions_v_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    sessions_h_scroll.pack(side=tk.BOTTOM, fill=tk.X, padx=10)

    d.sessions_tree.bind("<Double-1>", d.show_session_details)

