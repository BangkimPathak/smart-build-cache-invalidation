"""
Core application logic demonstrating multi-module dependency relationships.
Used to validate smart build-cache invalidation and reverse dependency impact analysis.
"""

from typing import Dict, List, Any


class DataProcessor:
    """Base data transformation engine."""
    def clean_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for r in records:
            if r.get("active", True) and r.get("value") is not None:
                cleaned.append({
                    "id": r.get("id"),
                    "value": float(r.get("value")),
                    "normalized": round(float(r.get("value")) / 100.0, 4)
                })
        return cleaned

    def compute_aggregates(self, records: List[Dict[str, Any]]) -> Dict[str, float]:
        if not records:
            return {"count": 0, "sum": 0.0, "mean": 0.0}
        total = sum(r["value"] for r in records)
        count = len(records)
        return {
            "count": count,
            "sum": round(total, 2),
            "mean": round(total / count, 2)
        }


class ReportGenerator:
    """Generates business summaries. Directly depends on DataProcessor."""
    def __init__(self, processor: DataProcessor = None):
        self.processor = processor or DataProcessor()

    def generate_summary(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        cleaned = self.processor.clean_records(raw_data)
        metrics = self.processor.compute_aggregates(cleaned)
        return {
            "status": "SUCCESS",
            "records_processed": metrics["count"],
            "total_value": metrics["sum"],
            "average_value": metrics["mean"],
            "audit_passed": True
        }


class AnalyticsEngine:
    """Independent analytics module for forecasting (No dependency on DataProcessor)."""
    def compute_growth_rate(self, current: float, previous: float) -> float:
        if previous == 0:
            return 0.0
        return round(((current - previous) / previous) * 100.0, 2)
