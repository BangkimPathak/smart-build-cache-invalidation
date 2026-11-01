import pytest
from src.core import DataProcessor, ReportGenerator, AnalyticsEngine


def test_data_processor_clean():
    dp = DataProcessor()
    data = [
        {"id": 1, "value": 50, "active": True},
        {"id": 2, "value": None, "active": True},
        {"id": 3, "value": 150, "active": False},
        {"id": 4, "value": 200, "active": True}
    ]
    cleaned = dp.clean_records(data)
    assert len(cleaned) == 2
    assert cleaned[0]["id"] == 1
    assert cleaned[0]["normalized"] == 0.50
    assert cleaned[1]["id"] == 4
    assert cleaned[1]["normalized"] == 2.0


def test_data_processor_aggregates():
    dp = DataProcessor()
    cleaned = [
        {"id": 1, "value": 100.0},
        {"id": 2, "value": 200.0}
    ]
    metrics = dp.compute_aggregates(cleaned)
    assert metrics["count"] == 2
    assert metrics["sum"] == 300.0
    assert metrics["mean"] == 150.0


def test_report_generator_integration():
    rg = ReportGenerator()
    data = [
        {"id": 1, "value": 50, "active": True},
        {"id": 2, "value": 150, "active": True}
    ]
    report = rg.generate_summary(data)
    assert report["status"] == "SUCCESS"
    assert report["records_processed"] == 2
    assert report["total_value"] == 200.0
    assert report["average_value"] == 100.0
    assert report["audit_passed"] is True


def test_analytics_growth():
    ae = AnalyticsEngine()
    assert ae.compute_growth_rate(120, 100) == 20.0
    assert ae.compute_growth_rate(100, 0) == 0.0
    assert ae.compute_growth_rate(80, 100) == -20.0
