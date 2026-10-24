"""Chat page with independent generation and reflection model selection."""
import streamlit as st
from reflectai.config import provider_settings, app_settings
from reflectai.reflection.engine import run_reflection
from reflectai.storage.history import add_entry

def render():
    st.title("ReflectAI Chat")
    st.caption("Generate, review, and refine an answer using your selected providers.")
    providers = [k for k, v in provider_settings().get("providers", {}).items() if v.get("enabled")]
    if not providers:
        st.error("No enabled providers found in config/providers.yaml")
        return
    left, right = st.columns(2)
    with left:
        gen_provider = st.selectbox("Generation provider", providers, key="gen_provider")
        gen_default = "llama3.2" if gen_provider == "ollama" else "gpt-4o-mini"
        gen_model = st.text_input("Generation model", gen_default, key="gen_model")
    with right:
        rev_provider = st.selectbox("Reflection provider", providers, key="rev_provider")
        rev_default = "llama3.2" if rev_provider == "ollama" else "gpt-4o-mini"
        rev_model = st.text_input("Reflection model", rev_default, key="rev_model")
    max_rounds = st.slider("Maximum reflection rounds", 0, 5, int(app_settings().get("app", {}).get("max_reflection_rounds", 2)))
    prompt = st.text_area("Your prompt", height=180, placeholder="What would you like ReflectAI to do?")
    if st.button("Generate and reflect", type="primary", disabled=not prompt.strip()):
        try:
            with st.spinner("Generating and reviewing..."):
                result = run_reflection(prompt, gen_provider, gen_model, rev_provider, rev_model, max_rounds)
            st.subheader("Final answer")
            st.markdown(result.answer)
            with st.expander("Last reflection review"):
                st.write(result.review)
            st.caption(f"Reflection rounds: {result.rounds}")
            add_entry(prompt, result.answer, {"generation_provider": gen_provider, "generation_model": gen_model, "reflection_provider": rev_provider, "reflection_model": rev_model, "rounds": result.rounds})
        except Exception as exc:
            st.error(f"Request failed: {exc}")
            if gen_provider == "openai" or rev_provider == "openai":
                st.info("For OpenAI, set OPENAI_API_KEY in .env. For Ollama, ensure Ollama is running and the selected model is pulled.")
