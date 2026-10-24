"""Streamlit application entry point."""
import streamlit as st
from .pages import chat, model_settings, history, about

def main():
    st.set_page_config(page_title="ReflectAI", page_icon="🔁", layout="wide")
    st.sidebar.title("ReflectAI")
    page = st.sidebar.radio("Navigation", ["Chat", "Model settings", "History", "About"])
    if page == "Chat":
        chat.render()
    elif page == "Model settings":
        model_settings.render()
    elif page == "History":
        history.render()
    else:
        about.render()

if __name__ == "__main__":
    main()
