"""Model and workflow configuration overview."""
import streamlit as st
from reflectai.config import provider_settings, app_settings
from reflectai.providers.registry import list_models
from reflectai.providers.ollama import OllamaProvider


def _render_model_settings() -> None:
    st.title("تنظیمات مدل و اجرا")
    st.caption(f"اطلاعات مدل‌ها به‌صورت خودکار به‌روزرسانی می‌شود · آخرین بررسی: {__import__('time').strftime('%H:%M:%S')}")
    providers = provider_settings().get("providers", {})
    defaults = app_settings().get("defaults", {})
    app = app_settings().get("app", {})

    st.markdown("### وضعیت ارائه‌دهنده‌ها")
    cols = st.columns(max(1, len(providers)))
    for col, (name, cfg) in zip(cols, providers.items()):
        with col:
            enabled = bool(cfg.get("enabled"))
            st.markdown(f"<div class='rai-provider-card'><span class='rai-status-dot {'rai-status-ok' if enabled else 'rai-status-off'}'></span><strong>{name.title()}</strong><span class='rai-pill'>{'فعال' if enabled else 'غیرفعال'}</span><small>{cfg.get('base_url', 'API-compatible endpoint')}</small></div>", unsafe_allow_html=True)
            if name == "ollama" and enabled:
                try:
                    models = list_models("ollama")
                    st.caption(f"{len(models)} مدل نصب‌شده")
                    if models:
                        st.code("\n".join(models), language="text")
                except Exception as exc:
                    st.warning(f"مدل‌های Ollama خوانده نشدند: {exc}")

    st.markdown("### پیش‌فرض‌های پروژه")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**مدل تولید**")
        st.code(f"Provider: {defaults.get('generation_provider', '—')}\nModel: {defaults.get('generation_model', '—')}", language="text")
    with c2:
        st.markdown("**مدل بازبینی**")
        st.code(f"Provider: {defaults.get('reflection_provider', '—')}\nModel: {defaults.get('reflection_model', '—')}", language="text")

    st.markdown("### گردش کار")
    c1, c2 = st.columns(2)
    with c1: st.metric("حداکثر دور بازبینی پیش‌فرض", str(app.get("max_reflection_rounds", 2)))
    with c2: st.metric("ظرفیت تاریخچه", str(app.get("history_limit", 100)))
    st.info("مدل‌ها، Context Length، حداکثر توکن خروجی و تعداد دورهای بازبینی را برای هر درخواست در صفحهٔ گفت‌وگو تنظیم کن. مقادیر حساس مانند API key را فقط در فایل .env قرار بده.")
    with st.expander("نمایش تنظیمات YAML"):
        st.markdown("**config/providers.yaml**")
        st.json(provider_settings())
        st.markdown("**config/settings.yaml**")
        st.json(app_settings())
    with st.expander("مدیریت حافظهٔ Ollama"):
        st.caption("مدل‌های بارگذاری‌شده می‌توانند RAM یا VRAM مصرف کنند؛ تخلیهٔ آن‌ها سرویس را متوقف نمی‌کند.")
        if st.button("تخلیهٔ همهٔ مدل‌ها", key="settings_unload_models"):
            try:
                names = OllamaProvider().unload_all()
                st.success(f"درخواست تخلیه ارسال شد: {', '.join(names) if names else 'مدلی بارگذاری نشده بود.'}")
            except Exception as exc:
                st.error(str(exc))


@st.fragment(run_every="5s")
def _model_settings_live_fragment() -> None:
    _render_model_settings()


def render() -> None:
    _model_settings_live_fragment()
