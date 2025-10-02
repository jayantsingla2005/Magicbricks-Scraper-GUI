"""
Refresh and data loading extracted from advanced_dashboard.py
"""
from __future__ import annotations


def setup_auto_refresh(d):
    d.auto_refresh_enabled = True
    d.refresh_interval = 30000  # 30 seconds
    schedule_refresh(d)


def schedule_refresh(d):
    if d.auto_refresh_enabled:
        d.root.after(d.refresh_interval, lambda: auto_refresh(d))


def auto_refresh(d):
    try:
        refresh_data(d)
    except Exception as e:
        print(f"Auto-refresh error: {e}")
    finally:
        schedule_refresh(d)


def refresh_data(d):
    try:
        d.load_overview_data()
        d.load_sessions_data()
        d.load_error_data()
        d.load_analytics_data()
        d.update_performance_charts()
    except Exception as e:
        print(f"Data refresh error: {e}")

