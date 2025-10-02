"""
Overview and sessions data loaders extracted from advanced_dashboard.py
"""
from __future__ import annotations
import sqlite3
import tkinter as tk
from datetime import datetime


def load_overview_data(d):
    try:
        conn = sqlite3.connect(d.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scrape_sessions")
        total_sessions = cursor.fetchone()[0]
        d.total_sessions_var.set(str(total_sessions))

        cursor.execute("SELECT SUM(properties_found) FROM scrape_sessions WHERE properties_found IS NOT NULL")
        result = cursor.fetchone()
        total_properties = result[0] if result[0] else 0
        d.total_properties_var.set(f"{total_properties:,}")

        cursor.execute(
            """
            SELECT COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*)
            FROM scrape_sessions
            """
        )
        success_rate = cursor.fetchone()[0] or 0
        d.success_rate_var.set(f"{success_rate:.1f}%")

        cursor.execute(
            """
            SELECT AVG(properties_found * 60.0 /
                   ((JULIANDAY(end_timestamp) - JULIANDAY(start_timestamp)) * 24 * 60))
            FROM scrape_sessions
            WHERE end_timestamp IS NOT NULL AND properties_found > 0
            """
        )
        avg_speed = cursor.fetchone()[0] or 0
        d.avg_speed_var.set(f"{avg_speed:.1f}")
        conn.close()
    except Exception as e:
        print(f"Error loading overview data: {e}")
        d.total_sessions_var.set("Error")
        d.total_properties_var.set("Error")
        d.success_rate_var.set("Error")
        d.avg_speed_var.set("Error")


def load_sessions_data(d):
    try:
        conn = sqlite3.connect(d.db_path)
        cursor = conn.cursor()
        for item in d.recent_tree.get_children():
            d.recent_tree.delete(item)
        cursor.execute(
            """
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
            """
        )
        for row in cursor.fetchall():
            session_id, city, mode, properties, duration, status, start_time = row
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                formatted_start = start_dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                formatted_start = start_time[:16] if start_time else "Unknown"
            d.recent_tree.insert("", "end", values=(
                session_id, city, mode, properties or 0, duration, status, formatted_start
            ))
        conn.close()
    except Exception as e:
        print(f"Error loading sessions data: {e}")

