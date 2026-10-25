"""Interactive, read-only SQLite workspace."""
from pathlib import Path
import pandas as pd
import streamlit as st
from reflectai.tools.schema_inspector import inspect_schema
from reflectai.tools.sql_executor import execute_read_only
from reflectai.tools.chart_executor import build_chart

def render():
    st.title("SQLite Workspace")
    st.caption("Inspect a local SQLite database, run read-only queries, and visualize results.")
    db_path = st.text_input("SQLite database path", placeholder="/path/to/database.db")
    if not db_path.strip():
        st.info("Enter the path to a local SQLite database to get started.")
        return
    path = Path(db_path).expanduser()
    if not path.is_file():
        st.warning("The selected path is not an existing file.")
        return
    try:
        schema = inspect_schema(path)
    except Exception as exc:
        st.error(f"Could not inspect database: {exc}")
        return
    with st.expander("Database schema", expanded=True):
        if schema:
            st.json(schema)
        else:
            st.info("No user tables were found in this database.")
    query = st.text_area("Read-only SQL query", value="SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name", height=120)
    row_limit = st.slider("Maximum rows", 1, 5000, 500)
    timeout = st.slider("Time limit (seconds)", 1, 30, 3)
    if st.button("Run query", type="primary", disabled=not query.strip()):
        try:
            columns, rows = execute_read_only(path, query, limit=row_limit, timeout_seconds=timeout)
            frame = pd.DataFrame(rows, columns=columns)
            st.session_state["reflectai_sql_result"] = frame
            st.success(f"Query returned {len(frame)} row(s). Results are capped at {row_limit} rows.")
        except Exception as exc:
            st.error(f"Query failed: {exc}")
    frame = st.session_state.get("reflectai_sql_result")
    if isinstance(frame, pd.DataFrame):
        st.subheader("Query results")
        st.dataframe(frame, use_container_width=True)
        if len(frame.columns):
            st.download_button("Download CSV", frame.to_csv(index=False).encode("utf-8"), "reflectai-query-results.csv", "text/csv")
        if len(frame.columns) >= 1:
            st.subheader("Visualize results")
            chart_type = st.selectbox("Chart type", ["bar", "line", "scatter", "histogram"])
            x_col = st.selectbox("X column", list(frame.columns))
            y_options = [c for c in frame.columns if c != x_col]
            y_col = st.selectbox("Y column", y_options) if chart_type != "histogram" and y_options else None
            if st.button("Build chart", disabled=(chart_type != "histogram" and y_col is None)):
                try:
                    st.plotly_chart(build_chart(frame, chart_type, x_col, y_col), use_container_width=True)
                except Exception as exc:
                    st.error(f"Could not create chart: {exc}")
