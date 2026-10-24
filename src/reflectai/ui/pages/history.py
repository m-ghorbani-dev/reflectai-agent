import streamlit as st
from reflectai.storage.history import get_history

def render():
    st.title("History")
    entries = list(reversed(get_history()))
    if not entries:
        st.info("No saved requests yet.")
        return
    for entry in entries:
        title = entry.get("prompt", "Untitled request").strip().replace("\n", " ")
        with st.expander(title[:90] or "Empty request"):
            st.caption(entry.get("timestamp", ""))
            st.markdown(entry.get("answer", ""))
            if entry.get("metadata"):
                st.json(entry["metadata"])
