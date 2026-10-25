import pandas as pd
import pytest
from reflectai.tools.chart_executor import build_chart

def test_build_bar_chart():
    chart = build_chart(pd.DataFrame({"category": ["a", "b"], "value": [1, 2]}), "bar", "category", "value")
    assert chart.data

def test_histogram_does_not_require_y():
    chart = build_chart({"value": [1, 2, 3]}, "histogram", "value")
    assert chart.data

def test_missing_column_is_rejected():
    with pytest.raises(ValueError, match="not found"):
        build_chart({"x": [1]}, "bar", "x", "missing")
