import streamlit as st

def show_header():
    st.set_page_config(page_title="Podman Streamlit 🦭", page_icon="🦭", layout="wide")
    st.title("🦭 Podman Streamlit 🦭")
    st.markdown(
        """
        This app displays **Podman container information** in an organized and interactive way.
        """
    )