"""Interactive, read-only SQLite workspace with query insights and charts."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from reflectai.tools.schema_inspector import inspect_schema
from reflectai.tools.sql_executor import execute_read_only
from reflectai.tools.chart_executor import build_chart


def _render_sql_workspace() -> None:
    st.title("فضای کاری SQLite")
    st.caption(f"ساختار و وضعیت فایل هر ۵ ثانیه تازه می‌شود · آخرین بررسی: {__import__('time').strftime('%H:%M:%S')}")
    db_path = st.text_input("مسیر فایل SQLite", placeholder="/path/to/database.db", key="rai_sql_db_path")
    if not db_path.strip():
        st.info("برای شروع، مسیر یک فایل SQLite محلی را وارد کن.")
        return
    path = Path(db_path).expanduser()
    if not path.is_file():
        st.warning("فایل انتخاب‌شده وجود ندارد یا مسیر معتبر نیست.")
        return
    try:
        schema = inspect_schema(path)
    except Exception as exc:
        st.error(f"خواندن ساختار پایگاه داده ناموفق بود: {exc}")
        return

    table_count = len(schema) if isinstance(schema, (dict, list)) else 0
    c1, c2 = st.columns(2)
    with c1: st.metric("جداول شناسایی‌شده", table_count)
    with c2: st.metric("وضعیت فایل", "آمادهٔ خواندن")
    with st.expander("ساختار پایگاه داده", expanded=False):
        if schema: st.json(schema)
        else: st.info("جدول کاربری پیدا نشد.")

    st.markdown("### اجرای کوئری")
    query = st.text_area("کوئری SQL فقط‌خواندنی", value="SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name", height=130, key="rai_sql_query")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1: row_limit = st.select_slider("حداکثر ردیف", options=[100, 250, 500, 1000, 2500, 5000], value=500)
    with c2: timeout = st.slider("مهلت (ثانیه)", 1, 30, 3)
    with c3: st.caption("برای محافظت از داده‌ها، اجرای نوشتن/تغییر داده در این فضا مجاز نیست.")
    if st.button("▶ اجرای کوئری", type="primary", disabled=not query.strip(), use_container_width=True):
        try:
            columns, rows = execute_read_only(path, query, limit=row_limit, timeout_seconds=timeout)
            st.session_state["reflectai_sql_result"] = pd.DataFrame(rows, columns=columns)
            st.session_state["reflectai_sql_query_text"] = query
            st.success(f"کوئری اجرا شد؛ {len(rows)} ردیف بازگشت داده شد.")
        except Exception as exc:
            st.error(f"اجرای کوئری ناموفق بود: {exc}")

    frame = st.session_state.get("reflectai_sql_result")
    if isinstance(frame, pd.DataFrame):
        st.markdown("### نتایج")
        a, b, c = st.columns(3)
        with a: st.metric("ردیف‌ها", len(frame))
        with b: st.metric("ستون‌ها", len(frame.columns))
        with c: st.download_button("⬇ دریافت CSV", frame.to_csv(index=False).encode("utf-8-sig"), "reflectai-query-results.csv", "text/csv", use_container_width=True)
        tab_data, tab_chart, tab_query = st.tabs(["جدول داده‌ها", "نمودار", "کوئری اجراشده"])
        with tab_data:
            st.dataframe(frame, use_container_width=True, hide_index=True)
        with tab_chart:
            if len(frame.columns) and len(frame):
                chart_type = st.selectbox("نوع نمودار", ["bar", "line", "scatter", "histogram"], key="rai_sql_chart_type")
                x_col = st.selectbox("ستون محور X", list(frame.columns), key="rai_sql_x_col")
                y_options = [column for column in frame.columns if column != x_col]
                y_col = st.selectbox("ستون محور Y", y_options, key="rai_sql_y_col") if chart_type != "histogram" and y_options else None
                if st.button("ساخت نمودار", key="rai_sql_build_chart", disabled=(chart_type != "histogram" and y_col is None)):
                    try:
                        fig = build_chart(frame, chart_type, x_col, y_col)
                        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        st.session_state["reflectai_sql_chart"] = fig
                    except Exception as exc:
                        st.error(f"ساخت نمودار ناموفق بود: {exc}")
                chart = st.session_state.get("reflectai_sql_chart")
                if chart is not None:
                    st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": True})
            else:
                st.info("برای نمودار، کوئری باید داده و دست‌کم یک ستون برگرداند.")
        with tab_query:
            st.code(st.session_state.get("reflectai_sql_query_text", query), language="sql")


@st.fragment(run_every="5s")
def _sql_live_fragment() -> None:
    _render_sql_workspace()


def render() -> None:
    _sql_live_fragment()
