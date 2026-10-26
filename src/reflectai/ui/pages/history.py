"""Local conversation history with summary charts and expandable traces."""
import pandas as pd
import plotly.express as px
import streamlit as st
from reflectai.storage.history import get_history, clear_history


def render() -> None:
    st.title("تاریخچهٔ مکالمات")
    st.caption("پاسخ‌ها به‌صورت محلی در پروژه ذخیره می‌شوند.")
    entries = list(reversed(get_history()))
    if not entries:
        st.info("هنوز پاسخی ذخیره نشده است.")
        return
    durations = []
    for entry in entries:
        metadata = entry.get("metadata") or {}
        try:
            duration = float(metadata.get("duration_seconds"))
        except (TypeError, ValueError):
            duration = None
        durations.append(duration)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("تعداد مکالمات", len(entries))
    with c2: st.metric("دارای زمان ثبت‌شده", sum(x is not None for x in durations))
    with c3: st.metric("میانگین زمان ثبت‌شده", f"{sum(x for x in durations if x is not None)/max(1, sum(x is not None for x in durations)):.1f} ثانیه")

    chart_rows = [{"مکالمه": f"#{i+1}", "ثانیه": duration} for i, duration in enumerate(durations) if duration is not None]
    if chart_rows:
        frame = pd.DataFrame(chart_rows)
        fig = px.bar(frame, x="مکالمه", y="ثانیه", title="زمان اجرا برای مکالمات ذخیره‌شده", template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=12, r=12, t=48, b=12))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with st.expander("⚠️ پاک‌کردن تاریخچه"):
        st.warning("این عملیات فایل تاریخچهٔ محلی را حذف می‌کند و قابل بازگشت نیست.")
        confirm = st.checkbox("حذف همهٔ مکالمات ذخیره‌شده را تأیید می‌کنم.", key="confirm_clear_history")
        if st.button("پاک‌کردن همهٔ تاریخچه", type="secondary", disabled=not confirm):
            clear_history()
            st.success("تاریخچه پاک شد.")
            st.rerun()

    st.markdown("### مکالمات")
    for index, entry in enumerate(entries):
        prompt = " ".join(entry.get("prompt", "درخواست بدون عنوان").split())
        metadata = entry.get("metadata") or {}
        with st.expander(f"{index+1:02d} · {prompt[:105] or 'درخواست بدون عنوان'}"):
            st.caption(entry.get("timestamp", ""))
            if metadata:
                cols = st.columns(4)
                fields = [("مدل تولید", metadata.get("generation_model")), ("مدل بازبینی", metadata.get("reflection_model")), ("دورهای بازبینی", metadata.get("rounds")), ("زمان اجرا", f"{metadata['duration_seconds']:.1f} ثانیه" if isinstance(metadata.get("duration_seconds"), (int, float)) else None)]
                for col, (label, value) in zip(cols, fields):
                    with col: st.metric(label, str(value) if value is not None else "—")
            st.markdown("**درخواست**")
            st.markdown(prompt)
            st.markdown("**پاسخ نهایی**")
            st.markdown(entry.get("answer", ""))
            trace = metadata.get("trace") or []
            if trace:
                with st.expander("مشاهدهٔ Reflection Trace"):
                    for step_no, step in enumerate(trace, 1):
                        with st.expander(f"{step_no}. {step.get('stage', 'مرحله')} · {step.get('model', '')}"):
                            if step.get("prompt") is not None:
                                st.markdown("**پرامپت**")
                                st.code(step["prompt"], language="text")
                            if step.get("response") is not None:
                                st.markdown("**پاسخ**")
                                st.code(step["response"], language="text")
