"""Validate and build charts from tabular data."""
import pandas as pd
import plotly.express as px

_CHARTS = {"bar": px.bar, "line": px.line, "scatter": px.scatter, "histogram": px.histogram}

def build_chart(data, chart_type: str, x: str, y: str | None = None):
    frame = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    kind = chart_type.strip().lower()
    if kind not in _CHARTS:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    required = [x] if kind == "histogram" else [x, y]
    missing = [column for column in required if not column or column not in frame.columns]
    if missing:
        raise ValueError(f"Column(s) not found: {', '.join(missing)}")
    kwargs = {"data_frame": frame, "x": x}
    if kind != "histogram":
        kwargs["y"] = y
    return _CHARTS[kind](**kwargs)
