"""Low-overhead Linux and Ollama resource monitoring and controls."""
import subprocess
import time
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
from reflectai.providers.ollama import OllamaProvider


def _read_cpu_sample():
    try:
        fields = Path('/proc/stat').read_text().splitlines()[0].split()[1:]
        values = [int(x) for x in fields]
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        return sum(values), idle
    except (OSError, ValueError, IndexError):
        return None


def read_system_metrics() -> dict:
    result = {"ram_used_gb": 0.0, "ram_total_gb": 0.0, "ram_percent": 0.0, "cpu_percent": None, "gpu": None}
    try:
        values = {}
        for line in Path('/proc/meminfo').read_text().splitlines():
            key, rest = line.split(':', 1)
            values[key] = int(rest.strip().split()[0])
        total = values.get('MemTotal', 0)
        available = values.get('MemAvailable', values.get('MemFree', 0))
        used = max(0, total - available)
        result.update(ram_total_gb=total / 1024 / 1024, ram_used_gb=used / 1024 / 1024,
                      ram_percent=(used / total * 100 if total else 0))
    except (OSError, ValueError):
        pass
    first = _read_cpu_sample()
    if first:
        time.sleep(0.12)
        second = _read_cpu_sample()
        if second:
            total_delta = second[0] - first[0]
            idle_delta = second[1] - first[1]
            if total_delta > 0:
                result['cpu_percent'] = max(0.0, min(100.0, (total_delta - idle_delta) / total_delta * 100))
    try:
        proc = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'],
                              capture_output=True, text=True, timeout=1.5, check=True)
        first_line = proc.stdout.strip().splitlines()[0]
        util, used, total = [float(x.strip()) for x in first_line.split(',')[:3]]
        result['gpu'] = {'util': util, 'used_gb': used / 1024, 'total_gb': total / 1024}
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        pass
    return result


def _stop_ollama_service() -> tuple[bool, str]:
    """Try safe non-interactive service stop paths; never prompt for a password."""
    attempts = [(['systemctl', '--user', 'stop', 'ollama'], 'user service')]
    try:
        for cmd, label in attempts:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if proc.returncode == 0:
                return True, f"Ollama user service متوقف شد ({label})."
        proc = subprocess.run(['sudo', '-n', 'systemctl', 'stop', 'ollama'], capture_output=True, text=True, timeout=5)
        if proc.returncode == 0:
            return True, 'سرویس سیستمی Ollama متوقف شد.'
        return False, 'توقف سرویس ممکن نشد؛ مجوز systemd لازم است. از ترمینال با دسترسی مناسب متوقفش کن.'
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f'اجرای دستور توقف ممکن نشد: {exc}'


def _render_resources() -> None:
    st.title("مانیتور منابع و Ollama")
    st.caption("پایش زندهٔ کم‌مصرف؛ اطلاعات هر ۲ ثانیه به‌روزرسانی می‌شوند. ابزارهای سخت‌افزاری فقط در صورت دسترس‌پذیری نمایش داده می‌شوند.")
    st.caption(f"آخرین نمونه‌برداری: {time.strftime('%H:%M:%S')}")
    if st.button("↻ خواندن دوبارهٔ وضعیت", type="primary", key="resources_manual_refresh"):
        st.rerun()
    metrics = read_system_metrics()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("RAM مصرف‌شده", f"{metrics['ram_used_gb']:.2f} GB", f"از {metrics['ram_total_gb']:.2f} GB")
        st.progress(metrics['ram_percent'] / 100, text=f"{metrics['ram_percent']:.1f}%")
    with c2:
        cpu = metrics['cpu_percent']
        st.metric("CPU", f"{cpu:.1f}%" if cpu is not None else "ناموجود")
        if cpu is not None: st.progress(max(0, min(100, cpu)) / 100)
    with c3:
        gpu = metrics['gpu']
        st.metric("GPU", f"{gpu['util']:.0f}%" if gpu else "ناموجود", f"VRAM: {gpu['used_gb']:.2f}/{gpu['total_gb']:.2f} GB" if gpu else "nvidia-smi در دسترس نیست")
        if gpu: st.progress(max(0, min(100, gpu['util'])) / 100)

    st.markdown("### وضعیت Ollama")
    try:
        provider = OllamaProvider()
        loaded = provider.loaded_models()
        installed = provider.list_models()
        st.success("Ollama API در دسترس است.")
        a, b = st.columns(2)
        with a:
            st.markdown("**مدل‌های نصب‌شده**")
            st.write(installed or "مدل نصب‌شده‌ای گزارش نشد.")
        with b:
            st.markdown("**مدل‌های بارگذاری‌شده در حافظه**")
            st.write(loaded or "مدلی در حافظه نیست.")
        if st.button("🧹 تخلیهٔ مدل‌های بارگذاری‌شده", use_container_width=True):
            try:
                names = provider.unload_all()
                st.success(f"درخواست تخلیه برای {len(names)} مدل ارسال شد." if names else "مدلی برای تخلیه نبود.")
                st.rerun()
            except Exception as exc:
                st.error(f"تخلیه ناموفق بود: {exc}")
    except Exception as exc:
        st.error(f"اتصال به Ollama برقرار نیست: {exc}")

    st.markdown("### کنترل سرویس")
    st.warning("توقف سرویس Ollama روی همهٔ برنامه‌های متصل به آن اثر می‌گذارد. اگر مدل دیگری از Ollama استفاده کند، آن هم قطع می‌شود.")
    confirm = st.checkbox("تأیید می‌کنم که می‌خواهم خود سرویس Ollama را متوقف کنم.", key="confirm_stop_ollama_service")
    if st.button("⏻ توقف سرویس Ollama", disabled=not confirm, type="secondary", use_container_width=True):
        ok, message = _stop_ollama_service()
        (st.success if ok else st.error)(message)

    st.markdown("### نحوهٔ خواندن شاخص‌ها")
    st.caption("RAM و CPU از اطلاعات لینوکس خوانده می‌شوند. GPU/VRAM فقط با nvidia-smi و درایور سازگار نمایش داده می‌شود. این صفحه خودکار و پرتکرار refresh نمی‌شود تا مصرف منابع اضافی ایجاد نکند.")


@st.fragment(run_every="2s")
def _resources_live_fragment() -> None:
    _render_resources()


def render() -> None:
    _resources_live_fragment()
