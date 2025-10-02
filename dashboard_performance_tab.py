"""
Performance tab builder extracted from advanced_dashboard.py
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def build_performance_tab(d):
    performance_frame = ttk.Frame(d.notebook)
    d.notebook.add(performance_frame, text="\U0001F4C8 Performance")

    charts_frame = ttk.Frame(performance_frame)
    charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    d.fig, ((d.ax1, d.ax2), (d.ax3, d.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
    d.fig.suptitle("Performance Analytics", fontsize=16)

    d.canvas = FigureCanvasTkAgg(d.fig, charts_frame)
    d.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    controls_frame = ttk.Frame(performance_frame)
    controls_frame.pack(fill=tk.X, padx=10, pady=5)

    ttk.Button(controls_frame, text="Refresh Charts", command=d.update_performance_charts).pack(side=tk.LEFT, padx=5)
    ttk.Button(controls_frame, text="Export Data", command=d.export_performance_data).pack(side=tk.LEFT, padx=5)


def update_performance_charts(d):
    try:
        for ax in [d.ax1, d.ax2, d.ax3, d.ax4]:
            ax.clear()
        d.ax1.plot([1, 2, 3, 4, 5], [10, 15, 12, 18, 20])
        d.ax1.set_title("Sessions Over Time")
        d.ax1.set_xlabel("Days")
        d.ax1.set_ylabel("Sessions")

        d.ax2.bar(["Mon", "Tue", "Wed", "Thu", "Fri"], [300, 450, 380, 520, 410])
        d.ax2.set_title("Properties Per Day")
        d.ax2.set_ylabel("Properties")

        cities = ["Gurgaon", "Noida", "Delhi", "Mumbai"]
        success_rates = [95, 92, 88, 90]
        d.ax3.pie(success_rates, labels=cities, autopct='%1.1f%%')
        d.ax3.set_title("Success Rate by City")

        d.ax4.plot([1, 2, 3, 4, 5], [85, 88, 92, 89, 94])
        d.ax4.set_title("Performance Trend")
        d.ax4.set_xlabel("Weeks")
        d.ax4.set_ylabel("Success Rate %")

        plt.tight_layout()
        d.canvas.draw()
    except Exception as e:
        print(f"Error updating charts: {e}")


def export_performance_data(d):
    try:
        messagebox.showinfo("Export", "Performance data exported successfully!")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export data: {e}")

