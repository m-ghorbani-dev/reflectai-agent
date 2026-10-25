"""Streamlit application entry point with a consistent dark-only shell."""
import streamlit as st
from .styles import inject_global_styles
from .pages import about, chat, dashboard, history, model_settings, resources, sql_workspace


def main() -> None:
    st.set_page_config(
        page_title="ReflectAI",
        page_icon="🔁",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={"About": "ReflectAI — local-first assistant with reflection and resource controls."},
    )
    inject_global_styles()
    with st.sidebar:
        st.markdown("<div class='rai-brand'><div class='rai-brand-icon'>R</div><div><strong>ReflectAI</strong><small>Reflect · Review · Improve</small></div></div>", unsafe_allow_html=True)
        st.markdown("<div class='rai-sidebar-label'>WORKSPACE</div>", unsafe_allow_html=True)
        page = st.radio(
            "ناوبری",
            ["داشبورد", "گفت‌وگو", "مانیتور منابع", "فضای SQLite", "تنظیمات مدل", "تاریخچه", "دربارهٔ برنامه"],
            label_visibility="collapsed",
            key="rai_navigation",
        )
        st.divider()
        _sidebar_live_status()
        st.markdown("<div class='rai-sidebar-footer'><span class='rai-live-dot'></span> رابط تیره · محلی</div>", unsafe_allow_html=True)

    routes = {
        "داشبورد": dashboard.render,
        "گفت‌وگو": chat.render,
        "مانیتور منابع": resources.render,
        "فضای SQLite": sql_workspace.render,
        "تنظیمات مدل": model_settings.render,
        "تاریخچه": history.render,
        "دربارهٔ برنامه": about.render,
    }
    routes[page]()


if __name__ == "__main__":
    main()
