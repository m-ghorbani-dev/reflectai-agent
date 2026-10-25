"""Create an example Plotly chart and save it as HTML."""
import pandas as pd
from reflectai.tools.chart_executor import build_chart

if __name__ == "__main__":
    frame = pd.DataFrame({"month": ["Jan", "Feb", "Mar"], "sales": [12, 18, 15]})
    chart = build_chart(frame, "bar", "month", "sales")
    chart.write_html("reflectai-example-chart.html", include_plotlyjs="cdn")
    print("Saved reflectai-example-chart.html")
