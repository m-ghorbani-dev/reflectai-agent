"""Overview dashboard for ReflectAI activity and local system resources."""
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
from reflectai.storage.history import get_history
from reflectai.observability.usage import usage_summary
from reflectai.providers.ollama import OllamaProvider
from .resources import read_system_metrics


def _metric(label: str, value: str, note: str = "") -> None:
    st.metric(label, value, help=note or None)


def _render_dashboard() -> None:
    st.title("ReflectAI · Overview")
    st.caption("نمای کلی فعالیت مدل‌ها، اجرای Reflection و وضعیت منابع سیستم")
    if st.button("↻ به‌روزرسانی وضعیت", key="dashboard_refresh"):
        st.rerun()

    history = get_history()
    task = st.session_state.get("reflectai_task", {})
    task_status = task.get("status", "idle")
    try:
        loaded = OllamaProvider().loaded_models()
        ollama_status = "متصل" if loaded is not None else "نامشخص"
    except Exception:
        loaded = []
        ollama_status = "در دسترس نیست"
    metrics = read_system_metrics()

    cols = st.columns(4)
    with cols[0]: _metric("گفت‌وگوهای ذخیره‌شده", str(len(history)), "تعداد ورودی‌های تاریخچهٔ محلی")
    with cols[1]: _metric("وضعیت اجرا", {"running":"در حال اجرا", "cancelling":"در حال توقف", "complete":"تکمیل‌شده", "cancelled":"متوقف‌شده", "error":"خطا"}.get(task_status, "آماده"))
    with cols[2]: _metric("مدل‌های بارگذاری‌شده", str(len(loaded)), "مدل‌هایی که Ollama در حال حاضر در حافظه نگه داشته است")
    with cols[3]: _metric("Ollama", ollama_status)

    st.markdown("### مصرف منابع سیستم")
    c1, c2, c3 = st.columns(3)
    with c1:
        _metric("RAM", f"{metrics['ram_used_gb']:.1f} / {metrics['ram_total_gb']:.1f} GB", "مقادیر از /proc/meminfo در لینوکس خوانده می‌شوند")
        st.progress(metrics["ram_percent"] / 100, text=f"{metrics['ram_percent']:.0f}% استفاده")
    with c2:
        cpu = metrics.get("cpu_percent")
        _metric("CPU", f"{cpu:.0f}%" if cpu is not None else "در دسترس نیست", "برآورد از دو نمونهٔ کوتاه /proc/stat")
        if cpu is not None:
            st.progress(max(0, min(100, cpu)) / 100, text=f"{cpu:.0f}% استفاده")
    with c3:
        gpu = metrics.get("gpu")
        _metric("GPU / VRAM", f"{gpu['util']}% · {gpu['used_gb']:.1f}/{gpu['total_gb']:.1f} GB" if gpu else "NVIDIA GPU در دسترس نیست", "اطلاعات nvidia-smi در صورت نصب بودن ابزار")
        if gpu:
            st.progress(max(0, min(100, gpu['util'])) / 100, text=f"GPU {gpu['util']}%")

    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("### مدل‌های در حافظه")
        if loaded:
            for model in loaded:
                st.markdown(f"<div class='rai-model-row'><span class='rai-live-dot'></span><strong>{model}</strong><span class='rai-pill'>بارگذاری‌شده</span></div>", unsafe_allow_html=True)
        else:
            st.info("در حال حاضر مدلی در حافظهٔ Ollama گزارش نشده است.")
        with st.expander("مدیریت حافظهٔ Ollama"):
            st.caption("تخلیهٔ مدل‌ها با توقف کامل سرویس متفاوت است. تخلیه، سرویس Ollama را روشن نگه می‌دارد.")
            if st.button("🧹 تخلیهٔ همهٔ مدل‌ها", type="secondary", use_container_width=True):
                try:
                    names = OllamaProvider().unload_all()
                    st.success("درخواست تخلیه ارسال شد." if names else "مدلی برای تخلیه نبود.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"تخلیه ناموفق بود: {exc}")
    with right:
        st.markdown("### فعالیت اخیر")
        counts = usage_summary()
        total = sum(counts.values())
        _metric("فراخوانی مدل در این نشست", str(total), "شمارنده در حافظه است و با راه‌اندازی مجدد برنامه صفر می‌شود")
        if counts:
            fig = go.Figure(go.Bar(x=list(counts.keys()), y=list(counts.values()), marker_color="#8b9cff"))
            fig.update_layout(height=230, margin=dict(l=12, r=12, t=12, b=45), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#edf2ff", xaxis_title="Provider / outcome", yaxis_title="تعداد")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.caption("هنوز فراخوانی‌ای در این نشست ثبت نشده است.")

    st.markdown("### آخرین مکالمات")
    if not history:
        st.info("پس از اولین پاسخ، تاریخچه در این قسمت نمایش داده می‌شود.")
    else:
        for entry in reversed(history[-5:]):
            prompt = " ".join(entry.get("prompt", "").split())
            with st.expander(prompt[:100] or "درخواست بدون عنوان"):
                st.caption(entry.get("timestamp", ""))
                st.markdown(entry.get("answer", ""))


@st.fragment(run_every="2s")
def _dashboard_live_fragment() -> None:
    _render_dashboard()


def render() -> None:
    _dashboard_live_fragment()
