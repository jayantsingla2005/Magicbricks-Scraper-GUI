"""
Errors tab builder extracted from advanced_dashboard.py
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk


def build_errors_tab(d):
    errors_frame = ttk.Frame(d.notebook)
    d.notebook.add(errors_frame, text="\u26a0\ufe0f Errors")

    error_summary_frame = ttk.LabelFrame(errors_frame, text="Error Summary", padding="10")
    error_summary_frame.pack(fill=tk.X, padx=10, pady=5)

    d.total_errors_var = tk.StringVar(value="Loading...")
    d.critical_errors_var = tk.StringVar(value="Loading...")
    d.recent_errors_var = tk.StringVar(value="Loading...")

    ttk.Label(error_summary_frame, text="Total Errors:").grid(row=0, column=0, sticky=tk.W)
    ttk.Label(error_summary_frame, textvariable=d.total_errors_var).grid(row=0, column=1, sticky=tk.W, padx=10)
    ttk.Label(error_summary_frame, text="Critical Errors:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
    ttk.Label(error_summary_frame, textvariable=d.critical_errors_var).grid(row=0, column=3, sticky=tk.W, padx=10)
    ttk.Label(error_summary_frame, text="Recent (24h):").grid(row=0, column=4, sticky=tk.W, padx=(20, 0))
    ttk.Label(error_summary_frame, textvariable=d.recent_errors_var).grid(row=0, column=5, sticky=tk.W, padx=10)

    error_columns = ("Timestamp", "Session ID", "Severity", "Category", "Message", "Details")
    d.errors_tree = ttk.Treeview(errors_frame, columns=error_columns, show="headings", height=15)
    for col in error_columns:
        d.errors_tree.heading(col, text=col)
        d.errors_tree.column(col, width=120)

    error_v_scroll = ttk.Scrollbar(errors_frame, orient=tk.VERTICAL, command=d.errors_tree.yview)
    d.errors_tree.configure(yscrollcommand=error_v_scroll.set)
    d.errors_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
    error_v_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)


def load_error_data(d):
    try:
        d.total_errors_var.set("0")
        d.critical_errors_var.set("0")
        d.recent_errors_var.set("0")
    except Exception as e:
        print(f"Error loading error data: {e}")

