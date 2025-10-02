"""
Analytics tab builder extracted from advanced_dashboard.py
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import sqlite3


def build_analytics_tab(d):
    analytics_frame = ttk.Frame(d.notebook)
    d.notebook.add(analytics_frame, text="\U0001F4CA Analytics")

    canvas = tk.Canvas(analytics_frame)
    scrollbar = ttk.Scrollbar(analytics_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    session_frame = ttk.LabelFrame(scrollable_frame, text="Session Analytics", padding="15")
    session_frame.pack(fill=tk.X, padx=10, pady=5)
    d.session_summary_text = tk.Text(session_frame, height=8, wrap=tk.WORD, font=("Consolas", 9))
    d.session_summary_text.pack(fill=tk.X, pady=5)

    perf_frame = ttk.LabelFrame(scrollable_frame, text="Performance Analytics", padding="15")
    perf_frame.pack(fill=tk.X, padx=10, pady=5)
    d.performance_text = tk.Text(perf_frame, height=8, wrap=tk.WORD, font=("Consolas", 9))
    d.performance_text.pack(fill=tk.X, pady=5)

    quality_frame = ttk.LabelFrame(scrollable_frame, text="Data Quality Analytics", padding="15")
    quality_frame.pack(fill=tk.X, padx=10, pady=5)
    d.quality_text = tk.Text(quality_frame, height=6, wrap=tk.WORD, font=("Consolas", 9))
    d.quality_text.pack(fill=tk.X, pady=5)

    canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
    scrollbar.pack(side="right", fill="y", pady=10)

    d.load_analytics_data()


def load_analytics_data(d):
    try:
        conn = sqlite3.connect(d.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                COUNT(CASE WHEN status = 'running' THEN 1 END) as running_sessions,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sessions,
                AVG(properties_found) as avg_properties,
                SUM(properties_found) as total_properties,
                AVG(pages_scraped) as avg_pages
            FROM scrape_sessions
            """
        )
        session_stats = cursor.fetchone()

        session_text = (
            f"SESSION SUMMARY\n"
            f"Total Sessions: {session_stats[0]}\n"
            f"Completed: {session_stats[1]} ({session_stats[1]/session_stats[0]*100:.1f}%)\n"
            f"Running: {session_stats[2]}\n"
            f"Failed: {session_stats[3]} ({session_stats[3]/session_stats[0]*100:.1f}%)\n\n"
            f"PROPERTY STATISTICS\n"
            f"Total Properties Scraped: {session_stats[5]:,}\n"
            f"Average Properties per Session: {session_stats[4]:.1f}\n"
            f"Average Pages per Session: {session_stats[6]:.1f}\n"
        )
        d.session_summary_text.delete(1.0, tk.END)
        d.session_summary_text.insert(1.0, session_text)

        cursor.execute(
            """
            SELECT
                scrape_mode,
                COUNT(*) as session_count,
                AVG(properties_found) as avg_properties,
                AVG(pages_scraped) as avg_pages,
                AVG((JULIANDAY(end_timestamp) - JULIANDAY(start_timestamp)) * 24 * 60) as avg_duration_minutes
            FROM scrape_sessions
            WHERE end_timestamp IS NOT NULL
            GROUP BY scrape_mode
            """
        )
        perf_data = cursor.fetchall()

        perf_text = "PERFORMANCE BY MODE\n"
        for mode, count, avg_props, avg_pages, avg_duration in perf_data:
            perf_text += (
                f"\n{mode.upper()} MODE:\n"
                f"  Sessions: {count}\n"
                f"  Avg Properties: {avg_props:.1f}\n"
                f"  Avg Pages: {avg_pages:.1f}\n"
                f"  Avg Duration: {avg_duration:.1f} minutes\n"
            )
            if avg_duration > 0:
                perf_text += f"  Speed: {avg_props/avg_duration:.2f} props/min\n"

        d.performance_text.delete(1.0, tk.END)
        d.performance_text.insert(1.0, perf_text)

        cursor.execute(
            """
            SELECT
                city,
                COUNT(*) as sessions,
                SUM(properties_found) as total_properties,
                AVG(properties_found) as avg_properties
            FROM scrape_sessions
            GROUP BY city
            ORDER BY total_properties DESC
            """
        )
        city_data = cursor.fetchall()

        quality_text = "CITY PERFORMANCE\n"
        for city, sessions, total_props, avg_props in city_data:
            quality_text += (
                f"\n{city.upper()}:\n"
                f"  Sessions: {sessions}\n"
                f"  Total Properties: {total_props:,}\n"
                f"  Avg per Session: {avg_props:.1f}\n"
            )

        d.quality_text.delete(1.0, tk.END)
        d.quality_text.insert(1.0, quality_text)
        conn.close()
    except Exception as e:
        print(f"Error loading analytics data: {e}")
        for text_widget in [d.session_summary_text, d.performance_text, d.quality_text]:
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, f"Error loading data: {e}")

