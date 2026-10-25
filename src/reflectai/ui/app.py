"""Streamlit application entry point."""
import streamlit as st
from .styles import inject_global_styles
from .pages import chat, model_settings, history, about, sql_workspace


def main():
    st.set_page_config(page_title="ReflectAI", page_icon="🔁", layout="wide", initial_sidebar_state="expanded")
    inject_global_styles()
    st.sidebar.title("ReflectAI")
    st.sidebar.caption("Reflect • Review • Improve")
    page = st.sidebar.radio("Navigation", ["Chat", "SQLite Workspace", "Model settings", "History", "About"])
    if page == "Chat":
        chat.render()
    elif page == "SQLite Workspace":
        sql_workspace.render()
    elif page == "Model settings":
        model_settings.render()
    elif page == "History":
        history.render()
    else:
        about.render()


if __name__ == "__main__":
    main()
