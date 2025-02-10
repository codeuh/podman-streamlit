import streamlit as st

def show():
    st.set_page_config(page_title="Podman Streamlit 🦭", page_icon="🦭", layout="wide")
    st.title("🦭 Podman 🦭 Streamlit 🦭")
    st.markdown(
        """
        This app was developed by [codeuh](https://github.com/codeuh) as a way to learn more about [Streamlit](https://streamlit.io/) and [Podman](https://podman.io/).
        """
    )