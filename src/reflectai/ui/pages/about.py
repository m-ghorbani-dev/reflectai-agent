import streamlit as st

def render():
    st.title("About ReflectAI")
    st.write("ReflectAI is an experimental multi-provider agent with an iterative review-and-revision workflow.")
    st.markdown("""
    **Current capabilities**
    - Select generation and reflection provider/model independently.
    - Run a bounded reflection loop.
    - Store recent prompts and answers locally.
    - Apply a basic read-only SQL guard for future SQL workflows.

    **Security note:** Do not use untrusted databases or expose this development UI to the public internet without additional security review.
    """)
