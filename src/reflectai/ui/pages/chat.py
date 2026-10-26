"""Chat page with model discovery and inspectable reflection trace."""
import streamlit as st
import threading
import time
from reflectai.providers.ollama import OllamaProvider
from reflectai.exceptions import GenerationCancelled
from reflectai.config import provider_settings, app_settings
from reflectai.providers.registry import list_models
from reflectai.reflection.engine import run_reflection
from reflectai.storage.history import add_entry
from reflectai.storage.answers import save_answer


def _set_chat_prompt(prompt: str) -> None:
    """Set the prompt from a sample button callback before widgets rerun."""
    st.session_state["chat_prompt"] = prompt


def _model_picker(label: str, provider: str, key: str) -> str:
    if provider == "ollama":
        try:
            models = list_models("ollama")
            if models:
                current = st.session_state.get(key)
                index = models.index(current) if current in models else 0
                return st.selectbox(label, models, index=index, key=key)
            st.warning("Ollama connected, but no local models were found. Run `ollama pull <model>`.")
        except Exception as exc:
            st.warning(f"Could not retrieve models from Ollama: {exc}")
            st.caption("Check that Ollama is running and accessible.")
    default = st.session_state.get(key, "gpt-4o-mini" if provider == "openai" else "")
    return st.text_input(f"{label} (enter model name)", value=default, key=f"{key}_manual")


def _render_trace(trace: list[dict]) -> None:
    st.subheader("Reflection Trace")
    st.caption("Actual prompts and model responses captured during this run. This shows exchanged messages, not hidden internal reasoning.")
    if not trace:
        st.info("No trace was recorded.")
        return
    stages = [item for item in trace if item.get("stage") != "final"]
    labels = {
        "generation": "📝 Generation",
        "reflection": "🔎 Reflection",
        "revision": "🛠️ Revision",
    }
    for start in range(0, len(stages), 3):
        row = stages[start:start + 3]
        cols = st.columns(len(row))
        for col, item in zip(cols, row):
            stage_label = labels.get(item.get("stage"), item.get("stage", "Step"))
            with col:
                st.markdown(
                    f"<div class='rai-trace-card'>"
                    f"<strong>{stage_label}</strong><br>"
                    f"<small>Round {item.get('round', 0)} · {item.get('model', '')}</small></div>",
                    unsafe_allow_html=True,
                )
        if start + 3 < len(stages):
            st.markdown("↓")
    st.markdown("**Inspect each stage below to see the exact prompts and responses.**")
    for index, item in enumerate(trace, 1):
        stage = item.get("stage", "step")
        round_number = item.get("round", 0)
        labels = {
            "generation": "Generation · initial answer",
            "reflection": f"Reflection · round {round_number}",
            "revision": f"Revision · round {round_number}",
            "final": "Final answer",
        }
        title = f"{index}. {labels.get(stage, stage)}"
        if item.get("model"):
            title += f" — {item.get('provider', '')} / {item['model']}"
        with st.expander(title, expanded=(index == 1)):
            if item.get("system_prompt"):
                st.markdown("**System prompt**")
                st.code(item["system_prompt"], language="text")
            if item.get("prompt") is not None:
                st.markdown("**Prompt sent to model**")
                st.code(item["prompt"], language="text")
            if item.get("response") is not None:
                st.markdown("**Model response / output**")
                st.code(item["response"], language="text")


def _install_persian_rtl() -> None:
    st.markdown("""
    <style>
    :root { --rai-ink:#e8eef8; --rai-muted:#9eacc2; --rai-panel:#111c2f; --rai-line:#293b56; --rai-accent:#7c9cff; }
    .stApp { background: radial-gradient(ellipse at top right, #1b2a48 0%, #0b1220 50%, #080d17 100%); }
    .block-container { max-width: 1450px; padding-top: 1.8rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { background: #0b1322; border-left: 1px solid var(--rai-line); }
    h1, h2, h3 { letter-spacing: -.02em; }
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stCaptionContainer"], .stApp label,
    .stApp [data-testid="stAlert"] { direction: rtl; text-align: right; }
    .stApp textarea, .stApp input { direction: rtl !important; text-align: right !important; }
    .stApp pre, .stApp code { direction: ltr !important; text-align: left !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--rai-line); border-radius: 16px; }
    .stButton > button { border-radius: 10px; border: 1px solid #344969; transition: all .15s ease; }
    .stButton > button:hover { border-color: var(--rai-accent); color: white; }
    .stButton > button[kind="primary"] { background: linear-gradient(100deg,#536dfe,#8b5cf6); border: 0; }
    div[data-testid="stMetric"] { background: #111c2f; padding: 12px 16px; border: 1px solid var(--rai-line); border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

def _live_progress_panel():
    """Return a callback that displays each completed model turn as it happens."""
    panel = st.empty()
    events = []
    labels = {"generation": "تولید پاسخ اولیه", "reflection": "ارزیابی پاسخ", "revision": "اصلاح پاسخ"}

    def update(event: dict) -> None:
        stage = event.get("stage", "step")
        round_no = event.get("round", 0)
        title = labels.get(stage, stage)
        if stage in ("reflection", "revision"):
            title += f" — دور {round_no}"
        if event.get("event") == "start":
            events.append({"title": title, "status": "در حال اجرا", "model": event.get("model", ""),
                           "prompt": event.get("prompt", ""), "system_prompt": event.get("system_prompt", ""), "response": None})
        else:
            found = next((item for item in reversed(events) if item["title"] == title and item["response"] is None), None)
            if found is None:
                found = {"title": title, "status": "تکمیل شد", "model": event.get("model", ""),
                         "prompt": event.get("prompt", ""), "system_prompt": event.get("system_prompt", ""), "response": None}
                events.append(found)
            found.update(status="تکمیل شد", response=event.get("response", ""))
        with panel.container():
            st.markdown("### 🔄 مراحل زندهٔ گفتگو بین مدل‌ها")
            st.caption("هر مرحله پس از دریافت پاسخ مدل نمایش داده می‌شود؛ زمان انتظار نیز مشخص است.")
            for item in events:
                icon = "⏳" if item["status"] == "در حال اجرا" else "✅"
                with st.expander(f"{icon} {item['title']} · {item['model']}", expanded=item["status"] == "در حال اجرا"):
                    st.markdown(f"**وضعیت:** {item['status']}")
                    if item.get("system_prompt"):
                        st.markdown("**System prompt**")
                        st.code(item["system_prompt"], language="text")
                    if item.get("prompt"):
                        st.markdown("**پرامپت ارسالی**")
                        st.code(item["prompt"], language="text")
                    if item.get("response") is not None:
                        st.markdown("**پاسخ مدل**")
                        st.markdown(item["response"] or "مدل پاسخ متنی برنگرداند.")
    return update


def _run_task(task: dict, prompt: str, gen_provider: str, gen_model: str,
              rev_provider: str, rev_model: str, max_rounds: int,
              context_len: int, max_tokens: int, unload_after: bool) -> None:
    try:
        from reflectai.reflection.engine import run_reflection
        result = run_reflection(
            prompt, gen_provider, gen_model, rev_provider, rev_model, max_rounds,
            progress_callback=lambda event: task["events"].append({**event, "time": time.time()}),
            context_len=context_len, max_tokens=max_tokens,
            cancel_event=task["cancel_event"], unload_after=unload_after,
        )
        task["result"] = result
        task["status"] = "cancelled" if task["cancel_event"].is_set() else "complete"
    except GenerationCancelled:
        task["status"] = "cancelled"
    except Exception as exc:
        task["error"] = str(exc)
        task["status"] = "error"
    finally:
        task["finished_at"] = time.time()
        if unload_after:
            # Also release any model left resident after a cancelled stream.
            try:
                OllamaProvider().unload_all()
            except Exception:
                pass


def _render_running_task():
    task = st.session_state.get("reflectai_task")
    if not task:
        return

    @st.fragment(run_every="1s")
    def task_monitor():
        current = st.session_state.get("reflectai_task")
        if not current:
            return
        status = current["status"]
        started = current["started_at"]
        elapsed = max(0, int(time.time() - started))
        if status == "running":
            st.warning(f"در حال اجرا — زمان سپری‌شده: {elapsed} ثانیه")
            if st.button("⏹ توقف فوری تولید", type="secondary", key="cancel_reflectai_run", use_container_width=True):
                current["cancel_event"].set()
                current["status"] = "cancelling"
                st.rerun()
        elif status == "cancelling":
            st.info("درخواست توقف ارسال شد؛ اتصال تولید در حال بسته‌شدن است…")
        elif status == "cancelled":
            st.warning("تولید متوقف شد. در صورت فعال بودن گزینهٔ تخلیه، مدل از حافظه آزاد می‌شود.")
        elif status == "error":
            st.error(f"اجرای مدل با خطا متوقف شد: {current.get('error', 'Unknown error')}")
        elif status == "complete":
            result = current.get("result")
            if result:
                st.success(f"پاسخ آماده شد · زمان اجرا: {elapsed} ثانیه")
                st.subheader("پاسخ نهایی")
                st.markdown(result.answer)
                st.caption(f"دورهای بازبینی: {result.rounds}")
                _render_trace(result.trace)
                if not current.get("saved"):
                    add_entry(current["prompt"], result.answer, {
                        "generation_provider": current["gen_provider"], "generation_model": current["gen_model"],
                        "reflection_provider": current["rev_provider"], "reflection_model": current["rev_model"],
                        "rounds": result.rounds, "trace": result.trace,
                        "context_len": current["context_len"], "max_tokens": current["max_tokens"],
                        "duration_seconds": max(0.0, time.time() - current["started_at"]),
                    })
                    try:
                        answer_path = save_answer(current["prompt"], result.answer, {
                            "generation_model": current["gen_model"],
                            "reflection_model": current["rev_model"],
                            "rounds": result.rounds,
                            "duration_seconds": round(max(0.0, time.time() - current["started_at"]), 2),
                        })
                        current["answer_file"] = str(answer_path)
                    except Exception as exc:
                        current["answer_save_error"] = str(exc)
                    current["saved"] = True
                if current.get("answer_file"):
                    st.success(f"پاسخ نهایی در فایل ذخیره شد: {current['answer_file']}")
                    st.download_button("دانلود پاسخ نهایی (.md)", data=result.answer, file_name="reflectai-answer.md",
                                       mime="text/markdown", key="download_final_answer")
                elif current.get("answer_save_error"):
                    st.warning(f"پاسخ نمایش داده شد، اما ذخیرهٔ فایل ناموفق بود: {current['answer_save_error']}")
            else:
                st.success("کار تمام شد.")
        events = list(current.get("events", []))
        if events:
            st.markdown("### مراحل زندهٔ اجرای مدل")
            total = max(1, 1 + 2 * current["max_rounds"])
            done_events = [event for event in events if event.get("event") == "complete"]
            done = len(done_events)
            progress = min(1.0, done / total)
            durations = []
            starts = {}
            for event in events:
                event_key = (event.get("stage"), event.get("round", 0))
                if event.get("event") == "start":
                    starts[event_key] = event.get("time")
                elif event.get("event") == "complete" and event_key in starts and event.get("time"):
                    durations.append(max(0.0, event["time"] - starts[event_key]))
            avg_step = sum(durations) / len(durations) if durations else None
            eta = int(avg_step * max(0, total - done)) if avg_step is not None else None
            progress_label = f"پیشرفت مراحل: {int(progress * 100)}٪ · {done} از حداکثر {total} مرحله"
            if eta is not None and status == "running":
                progress_label += f" · زمان باقی‌ماندهٔ تخمینی: حدود {eta} ثانیه"
            st.progress(progress, text=progress_label)
            labels = {"generation": "تولید پاسخ اولیه", "reflection": "بازبینی پاسخ", "revision": "اصلاح پاسخ"}
            for idx, event in enumerate(events, 1):
                title = labels.get(event.get("stage"), event.get("stage", "مرحله"))
                if event.get("round"):
                    title += f" — دور {event['round']}"
                icon = "⏳" if event.get("event") == "start" else "✅"
                with st.expander(f"{icon} {idx}. {title} · {event.get('model', '')}", expanded=event.get("event") == "start"):
                    st.caption(f"{event.get('provider', '')} / {event.get('model', '')}")
                    if event.get("system_prompt"):
                        st.markdown("**System prompt**")
                        st.code(event["system_prompt"], language="text")
                    if event.get("prompt"):
                        st.markdown("**پرامپت ارسالی**")
                        st.code(event["prompt"], language="text")
                    if event.get("response") is not None:
                        st.markdown("**پاسخ مدل**")
                        st.code(event["response"], language="text")
        if status in ("complete", "cancelled", "error"):
            if st.button("پاک‌کردن وضعیت اجرا", key="clear_reflectai_task"):
                st.session_state.pop("reflectai_task", None)
                st.rerun()

    task_monitor()


def render():
    st.title("گفت‌وگو با ReflectAI")
    st.caption("تولید، بازبینی و اصلاح پاسخ با کنترل منابع و مشاهدهٔ مراحل واقعی تبادل با مدل‌ها.")

    with st.sidebar:
        st.markdown("### ⚙️ کنترل منابع Ollama")
        st.caption("بستن تب مرورگر، سرور Ollama را متوقف نمی‌کند. این کنترل‌ها مدل‌های بارگذاری‌شده را تخلیه می‌کنند.")
        if st.button("🧹 آزادسازی حافظهٔ مدل‌ها", use_container_width=True, key="unload_ollama_models"):
            try:
                released = OllamaProvider().unload_all()
                st.success("درخواست تخلیه ارسال شد: " + (", ".join(released) if released else "مدلی در حافظه نبود."))
            except Exception as exc:
                st.error(f"ارتباط با Ollama برقرار نشد: {exc}")

    active_task = st.session_state.get("reflectai_task")
    if active_task and active_task.get("status") in ("running", "cancelling"):
        _render_running_task()
        return

    providers = [k for k, v in provider_settings().get("providers", {}).items() if v.get("enabled")]
    if not providers:
        st.error("No enabled providers found in config/providers.yaml")
        return
    left, right = st.columns(2, gap="large")
    with left:
        gen_provider = st.selectbox("مدل تولید پاسخ", providers, key="gen_provider")
        gen_model = _model_picker("Generation model", gen_provider, "gen_model")
    with right:
        rev_provider = st.selectbox("مدل بازبینی", providers, key="rev_provider")
        rev_model = _model_picker("Reflection model", rev_provider, "rev_model")

    with st.expander("تنظیمات پیشرفتهٔ تولید و مصرف حافظه", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            context_len = st.select_slider("Context length (توکن ورودی)", options=[512, 1024, 2048, 4096, 8192, 16384, 32768], value=4096,
                                           help="برای مصرف کمتر RAM/VRAM مقدار کوچک‌تری انتخاب کن.")
        with c2:
            max_tokens = st.slider("حداکثر توکن خروجی", min_value=128, max_value=4096, value=1024, step=128,
                                   help="حد بالای طول پاسخ هر فراخوانی مدل؛ برای پاسخ کوتاه‌تر کاهش بده.")
        with c3:
            max_rounds = st.slider("حداکثر دور بازبینی", 0, 5, int(app_settings().get("app", {}).get("max_reflection_rounds", 2)))
        unload_after = st.checkbox("پس از هر پاسخ، مدل Ollama از حافظه تخلیه شود", value=True,
                                   help="مصرف پایدار حافظه کمتر می‌شود، اما برای هر دور ممکن است مدل دوباره بارگذاری شود.")

    examples = [
        ("توضیح یک مفهوم", "بیش‌برازش (Overfitting) در یادگیری ماشین چیست؟ با یک مثال ساده توضیح بده و سه روش کاهش آن را فهرست کن."),
        ("بررسی کد پایتون", "تابعی در پایتون بنویس که بررسی کند رشته palindrome است یا نه. کد را کوتاه نگه دار، حالت‌های مرزی را در نظر بگیر و یک تست نمونه ارائه کن."),
        ("مقایسهٔ دو روش", "لیست (list) و تاپل (tuple) در پایتون را در یک جدول کوتاه مقایسه کن و برای هرکدام یک مثال بزن."),
        ("برنامهٔ یادگیری", "یک برنامهٔ ۷ روزه برای یادگیری SQL بنویس؛ برای هر روز فقط هدف و یک تمرین کوتاه ذکر کن."),
        ("ارزیابی انتقادی", "این ادعا را بررسی کن: «همبستگی همیشه رابطهٔ علت و معلولی را ثابت می‌کند.» پاسخ کوتاه، دقیق و همراه با یک مثال نقض باشد."),
    ]
    prompt_col, examples_col = st.columns([2, 1], gap="large")
    with prompt_col:
        prompt = st.text_area("پرامپت شما", height=210, placeholder="درخواست خود را بنویس یا نمونه‌ای را از سمت راست انتخاب کن.", key="chat_prompt")
    with examples_col:
        st.markdown("#### ✨ نمونه‌پرامپت‌های آماده")
        st.caption("برای قرار دادن نمونه در کادر کلیک کن.")
        for example_index, (example_label, example_prompt) in enumerate(examples):
            st.button(example_label, key=f"sample_prompt_{example_index}", use_container_width=True,
                      on_click=_set_chat_prompt, args=(example_prompt,))

    if st.button("▶ شروع تولید و بازبینی", type="primary", disabled=not prompt.strip(), use_container_width=True):
        task = {
            "status": "running", "started_at": time.time(), "events": [], "result": None,
            "error": None, "cancel_event": threading.Event(), "prompt": prompt,
            "gen_provider": gen_provider, "gen_model": gen_model,
            "rev_provider": rev_provider, "rev_model": rev_model,
            "max_rounds": max_rounds, "context_len": context_len,
            "max_tokens": max_tokens, "saved": False,
        }
        st.session_state["reflectai_task"] = task
        worker = threading.Thread(target=_run_task, args=(task, prompt, gen_provider, gen_model,
            rev_provider, rev_model, max_rounds, context_len, max_tokens,
            unload_after), daemon=True)
        task["thread"] = worker
        worker.start()
        st.rerun()

    _render_running_task()

