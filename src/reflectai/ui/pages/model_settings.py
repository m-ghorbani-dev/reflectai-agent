import streamlit as st
from reflectai.config import provider_settings, app_settings

def render():
    st.title("Model Settings")
    st.write("Provider settings are read from `config/providers.yaml`.")
    st.json(provider_settings())
    st.write("Application settings")
    st.json(app_settings())
    st.info("Choose generation and reflection providers/models on the Chat page. Put API credentials in `.env`, never in YAML or source code.")
