import streamlit as st


def render() -> None:
    st.title("دربارهٔ ReflectAI")
    st.markdown("""
    ReflectAI یک دستیار چندارائه‌دهنده‌ای است که پاسخ را تولید می‌کند، آن را بازبینی می‌کند و در صورت نیاز اصلاح می‌کند.
    """)
    cols = st.columns(3)
    with cols[0]:
        st.markdown("<div class='rai-provider-card'><h3>💬 گفت‌وگو</h3><p>تولید پاسخ با مدل انتخابی و نمونه‌پرامپت‌های آماده.</p></div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown("<div class='rai-provider-card'><h3>🔎 Reflection Trace</h3><p>مشاهدهٔ پیام‌ها و پاسخ‌های واقعی هر مرحله.</p></div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown("<div class='rai-provider-card'><h3>🧠 منابع محلی</h3><p>کنترل مدل‌های بارگذاری‌شده و بررسی RAM، CPU و VRAM.</p></div>", unsafe_allow_html=True)
    st.markdown("### قابلیت‌ها")
    st.markdown("""
    - انتخاب جداگانهٔ مدل تولید و مدل بازبینی.
    - گردش کار محدودشدهٔ تولید، بازبینی و اصلاح.
    - تاریخچهٔ محلی و Reflection Trace قابل بررسی.
    - فضای کاری SQLite فقط‌خواندنی، خروجی CSV و نمودارها.
    - مانیتور منابع لینوکس و مدیریت حافظهٔ Ollama.
    - رابط کاربری Dark Mode با چیدمان واکنش‌گرا.
    """)
    st.warning("خروجی مدل ممکن است اشتباه باشد. سرور Streamlit را مستقیماً در اینترنت عمومی منتشر نکن. ابزار توقف سرویس Ollama روی تمام برنامه‌های متصل به همان سرویس اثر می‌گذارد.")
