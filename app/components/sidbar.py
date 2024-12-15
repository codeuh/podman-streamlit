import streamlit as st

connections = {
    "Local User Podman Socket": "unix:///run/user/1000/podman/podman.sock"
}

def show_sidebar_socket_selector():
    selected_name = st.sidebar.selectbox(
        "Select Podman API Connection",
        options=list(connections.keys()),
        key="connection_selector"
    )

    selected_uri = connections[selected_name]

    if "selected_uri" not in st.session_state:
        st.session_state.selected_uri = selected_uri

    if st.session_state.selected_uri != selected_uri:
        st.session_state.selected_uri = selected_uri
        st.rerun()
    return selected_uri

def show_sidebar_details(client):
    st.sidebar.header("Podman Information")

    version = client.version()
    st.sidebar.metric("Release", version["Version"])
    st.sidebar.metric("Compatible API", version["ApiVersion"])
    st.sidebar.metric("OS", version["Components"][0]["Details"]["Os"])
    st.sidebar.metric("Arch", version["Arch"])
    st.sidebar.metric("Go Version", version["GoVersion"])