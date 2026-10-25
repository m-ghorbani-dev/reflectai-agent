"""Chat page with model discovery and inspectable reflection trace."""
import streamlit as st
import time
from reflectai.config import provider_settings, app_settings
from reflectai.providers.registry import list_models, unload_ollama_models
from reflectai.reflection.engine import run_reflection
from reflectai.storage.history import add_entry


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
                    f"<div style='border:1px solid #cbd5e1;border-radius:10px;padding:12px;min-height:78px'>"
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
    /* Improve Persian readability while preserving code and model prompts as LTR. */
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stCaptionContainer"],
    .stApp label,
    .stApp [data-testid="stAlert"] { direction: rtl; text-align: right; }
    .stApp textarea { direction: rtl !important; text-align: right !important; }
    .stApp input { direction: rtl; text-align: right; }
    .stApp pre, .stApp code { direction: ltr; text-align: left; }
    </style>
    """, unsafe_allow_html=True)


def _format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"حدود {seconds} ثانیه"
    minutes, remaining = divmod(seconds, 60)
    return f"حدود {minutes} دقیقه و {remaining} ثانیه"


def _live_progress_panel(max_rounds: int):
    """Show stage progress and a rough ETA while each model call runs."""
    panel = st.empty()
    events = []
    completed_durations = []
    active_started = None
    active_title = None
    started_at = time.monotonic()
    expected_calls = max(1, 1 + 2 * max_rounds)
    completed_calls = 0
    labels = {"generation": "تولید پاسخ اولیه", "reflection": "ارزیابی پاسخ", "revision": "اصلاح پاسخ"}

    def update(event: dict) -> None:
        nonlocal active_started, active_title, completed_calls
        if event.get("event") == "workflow_complete":
            elapsed = time.monotonic() - started_at
            with panel.container():
                st.markdown("### ✅ فرایند کامل شد")
                st.progress(1.0, text="پیشرفت: ۱۰۰٪")
                st.caption(f"زمان کل اجرا: {_format_duration(elapsed)}")
                for item in events:
                    icon = "✅" if item["status"] == "تکمیل شد" else "⏭️"
                    with st.expander(f"{icon} {item['title']} · {item['model']}", expanded=False):
                        st.markdown(f"**وضعیت:** {item['status']}")
                        if item.get("system_prompt"):
                            st.markdown("**پرامپت سیستمی**")
                            st.code(item["system_prompt"], language="text")
                        if item.get("prompt"):
                            st.markdown("**پرامپت ارسالی**")
                            st.code(item["prompt"], language="text")
                        if item.get("response") is not None:
                            st.markdown("**پاسخ مدل**")
                            st.markdown(item["response"] or "مدل پاسخ متنی برنگرداند.")
            return

        stage = event.get("stage", "step")
        round_no = event.get("round", 0)
        title = labels.get(stage, stage)
        if stage in ("reflection", "revision"):
            title += f" — دور {round_no}"
        now = time.monotonic()
        if event.get("event") == "start":
            active_started = now
            active_title = title
            events.append({"title": title, "status": "در حال اجرا", "model": event.get("model", ""),
                           "prompt": event.get("prompt", ""), "system_prompt": event.get("system_prompt", ""), "response": None})
        else:
            found = next((item for item in reversed(events) if item["title"] == title and item["response"] is None), None)
            if found is None:
                found = {"title": title, "status": "در حال اجرا", "model": event.get("model", ""),
                         "prompt": event.get("prompt", ""), "system_prompt": event.get("system_prompt", ""), "response": None}
                events.append(found)
            found.update(status="تکمیل شد", response=event.get("response", ""))
            if active_started is not None:
                completed_durations.append(max(0.1, now - active_started))
            completed_calls += 1
            active_started = None
            active_title = None

        elapsed = now - started_at
        average_call = sum(completed_durations) / len(completed_durations) if completed_durations else 15.0
        active_elapsed = now - active_started if active_started is not None else 0
        # ETA is intentionally approximate: model latency and early approval vary.
        remaining_calls = max(0, expected_calls - completed_calls - (1 if active_started is not None else 0))
        estimated_remaining = (max(0, average_call - active_elapsed) if active_started is not None else 0) + remaining_calls * average_call
        progress_fraction = min(0.97, (completed_calls + (0.5 if active_started is not None else 0)) / expected_calls)
        with panel.container():
            st.markdown("### 🔄 مراحل زندهٔ گفتگو بین مدل‌ها")
            st.progress(progress_fraction, text=f"پیشرفت تقریبی: {int(progress_fraction * 100)}٪")
            st.caption(f"زمان سپری‌شده: {_format_duration(elapsed)} · زمان باقی‌ماندهٔ تخمینی: { _format_duration(estimated_remaining) }")
            st.caption("زمان باقی‌مانده تقریبی است و بسته به سرعت مدل و تأیید زودهنگام پاسخ تغییر می‌کند.")
            for item in events:
                icon = "⏳" if item["status"] == "در حال اجرا" else "✅"
                with st.expander(f"{icon} {item['title']} · {item['model']}", expanded=item["status"] == "در حال اجرا"):
                    st.markdown(f"**وضعیت:** {item['status']}")
                    if item.get("system_prompt"):
                        st.markdown("**پرامپت سیستمی**")
                        st.code(item["system_prompt"], language="text")
                    if item.get("prompt"):
                        st.markdown("**پرامپت ارسالی**")
                        st.code(item["prompt"], language="text")
                    if item.get("response") is not None:
                        st.markdown("**پاسخ مدل**")
                        st.markdown(item["response"] or "مدل پاسخ متنی برنگرداند.")
    return update


def render():
    _install_persian_rtl()
    st.title("گفت‌وگو با ReflectAI")
    st.caption("با مدل‌های انتخاب‌شده پاسخ تولید کن، آن را ارزیابی کن و بهبود بده.")
    providers = [k for k, v in provider_settings().get("providers", {}).items() if v.get("enabled")]
    if not providers:
        st.error("No enabled providers found in config/providers.yaml")
        return
    left, right = st.columns(2)
    with left:
        gen_provider = st.selectbox("Generation provider", providers, key="gen_provider")
        gen_model = _model_picker("Generation model", gen_provider, "gen_model")
    with right:
        rev_provider = st.selectbox("Reflection provider", providers, key="rev_provider")
        rev_model = _model_picker("Reflection model", rev_provider, "rev_model")
    max_rounds = st.slider("Maximum reflection rounds", 0, 5, int(app_settings().get("app", {}).get("max_reflection_rounds", 2)))

    with st.expander("مدیریت منابع Ollama", expanded=False):
        st.caption("Ollama ممکن است مدل‌ها را پس از پایان درخواست در RAM/VRAM نگه دارد. این دکمه مدل‌های بارگذاری‌شده را از حافظه خارج می‌کند؛ خود سرویس Ollama روشن می‌ماند.")
        if st.button("آزادسازی حافظهٔ مدل‌های Ollama", key="unload_ollama_models"):
            try:
                unloaded = unload_ollama_models()
                if unloaded:
                    st.success("مدل‌های خارج‌شده از حافظه: " + ", ".join(unloaded))
                else:
                    st.info("مدلی در حال اجرا نبود؛ حافظه‌ای برای آزادسازی از طرف Ollama پیدا نشد.")
            except Exception as exc:
                st.error(f"آزادسازی مدل‌ها ناموفق بود: {exc}")

    # Clickable examples make it easier to try the app without writing a prompt first.
    examples = [
        ("توضیح یک مفهوم", "بیش‌برازش (Overfitting) در یادگیری ماشین چیست؟ با یک مثال ساده از زندگی واقعی توضیح بده و سه روش عملی برای کاهش آن ارائه کن."),
        ("بررسی کد پایتون", "یک تابع پایتون بنویس که بررسی کند آیا یک رشته از دو طرف یکسان خوانده می‌شود یا نه (Palindrome). حالت‌های مرزی را در نظر بگیر، سپس کد را از نظر خطا بررسی کن و در صورت نیاز بهبود بده."),
        ("مقایسهٔ دو روش", "لیست (list) و تاپل (tuple) در پایتون را مقایسه کن. برای هرکدام مثال بزن، توضیح بده چه زمانی باید از آن استفاده کرد و در پایان درستی فنی مقایسه را بررسی کن."),
        ("ساخت برنامهٔ یادگیری", "یک برنامهٔ ۷ روزه برای فرد مبتدی طراحی کن تا SQL را یاد بگیرد. برای هر روز هدف، یک تمرین کوتاه و روشی برای سنجش پیشرفت مشخص کن."),
        ("آزمایش ارزیابی انتقادی", "فردی می‌گوید: «همبستگی همیشه رابطهٔ علت و معلولی را ثابت می‌کند.» این ادعا را ارزیابی کن، اشکال آن را توضیح بده و یک مثال نقض روشن ارائه کن."),
    ]
    prompt_col, examples_col = st.columns([2, 1], gap="large")
    with prompt_col:
        prompt = st.text_area(
            "پرامپت شما", height=220,
            placeholder="درخواست خود را بنویس یا یکی از نمونه‌های سمت راست را انتخاب کن.",
            key="chat_prompt",
        )
    with examples_col:
        st.markdown("#### نمونه‌پرامپت‌های آماده")
        st.caption("یک نمونه را انتخاب کن تا متن آن در کادر پرامپت قرار بگیرد؛ پیش از اجرا می‌توانی آن را ویرایش کنی.")
        for example_index, (example_label, example_prompt) in enumerate(examples):
            st.button(
                example_label,
                key=f"sample_prompt_{example_index}",
                use_container_width=True,
                on_click=_set_chat_prompt,
                args=(example_prompt,),
            )

    if st.button("تولید پاسخ و بازبینی", type="primary", disabled=not prompt.strip()):
        try:
            progress_callback = _live_progress_panel(max_rounds)
            result = run_reflection(prompt, gen_provider, gen_model, rev_provider, rev_model, max_rounds, progress_callback=progress_callback)
            progress_callback({"event": "workflow_complete"})
            st.subheader("پاسخ نهایی")
            st.markdown(result.answer)
            st.caption(f"تعداد دورهای بازبینی: {result.rounds}")
            _render_trace(result.trace)
            add_entry(prompt, result.answer, {
                "generation_provider": gen_provider, "generation_model": gen_model,
                "reflection_provider": rev_provider, "reflection_model": rev_model,
                "rounds": result.rounds, "trace": result.trace,
            })
        except Exception as exc:
            st.error(f"Request failed: {exc}")
            if gen_provider == "openai" or rev_provider == "openai":
                st.info("For OpenAI, set OPENAI_API_KEY in .env. For Ollama, ensure Ollama is running and the selected model is pulled.")
