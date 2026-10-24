"""Build a Plotly chart from tabular data."""
import pandas as pd
import plotly.express as px

def make_chart(data, chart_type: str, x: str, y: str):
    frame = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    if x not in frame.columns or y not in frame.columns:
        raise ValueError("Selected x/y columns are not present in the data.")
    if chart_type == "Bar":
        return px.bar(frame, x=x, y=y)
    if chart_type == "Line":
        return px.line(frame, x=x, y=y)
    if chart_type == "Scatter":
        return px.scatter(frame, x=x, y=y)
    if chart_type == "Histogram":
        return px.histogram(frame, x=x)
    raise ValueError(f"Unsupported chart type: {chart_type}")
