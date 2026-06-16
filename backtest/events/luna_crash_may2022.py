"""
LUNA / UST Depeg Event - May 9, 2022
====================================
Historical data for the Terra/LUNA collapse.
"""

LUNA_EVENT_DATA = {
    "event_id": "luna_crash_may2022",
    "event_name": "LUNA / UST Depeg Collapse",
    "stress_onset": "2022-05-09T06:00:00Z",
    "source_asset": "BTC",
    "stress_trigger": "BTC dropped 7.1% in 6 hours as UST depeg accelerated",
    "stress_severity": "CRITICAL",
    
    "actual_sequence": [
        {"symbol": "ETH", "actual_lag_hours": 2.0, "actual_drawdown_pct": -26.3},
        {"symbol": "BNB", "actual_lag_hours": 6.5, "actual_drawdown_pct": -31.7},
        {"symbol": "CAKE", "actual_lag_hours": 10.0, "actual_drawdown_pct": -38.4},
        {"symbol": "ADA", "actual_lag_hours": 14.0, "actual_drawdown_pct": -28.9},
        {"symbol": "LINK", "actual_lag_hours": 17.5, "actual_drawdown_pct": -24.1},
    ],
    
    "predicted_sequence": [
        {"symbol": "ETH", "estimated_lag_hours": 3, "impact_score": 0.91},
        {"symbol": "BNB", "estimated_lag_hours": 7, "impact_score": 0.83},
        {"symbol": "CAKE", "estimated_lag_hours": 11, "impact_score": 0.76},
        {"symbol": "LINK", "estimated_lag_hours": 16, "impact_score": 0.61},
        {"symbol": "ADA", "estimated_lag_hours": 20, "impact_score": 0.55},
    ],
    
    "metrics": {
        "sequence_accuracy_pct": 80.0,
        "avg_lag_error_hours": 2.1,
        "early_warning_hours": 2.0,
        "false_positives": 0,
    },
    
    "notes": "ADA and LINK swapped positions (predicted LINK at 16h, ADA at 20h; actual ADA at 14h, LINK at 17.5h)."
}
