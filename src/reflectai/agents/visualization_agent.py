"""Build a Plotly chart from tabular data."""
from ..tools.chart_executor import build_chart

def make_chart(data, chart_type: str, x: str, y: str | None = None):
    names = {"Bar": "bar", "Line": "line", "Scatter": "scatter", "Histogram": "histogram"}
    return build_chart(data, names.get(chart_type, chart_type), x, y)
