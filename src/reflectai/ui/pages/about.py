import streamlit as st

def render():
    st.title("About ReflectAI")
    st.write("ReflectAI is a local-first multi-provider assistant with iterative review, local request history, and a read-only SQLite workspace.")
    st.markdown("""
    **Capabilities**
    - Select generation and reflection providers/models independently.
    - Run a bounded generate-review-revise workflow.
    - Store recent prompts and answers locally.
    - Query SQLite databases through a read-only connection with an authorizer, row cap, and execution deadline.
    - Inspect database schemas, export query results to CSV, and visualize query results.
    - Use Ollama locally or an OpenAI-compatible API.

    **Security limitations**
    - Review output is model-generated and is not a guarantee of correctness.
    - Do not expose the Streamlit development server directly to the public internet.
    - Database files are accessed with the operating system permissions of the running process; only open databases you trust.
    """)
