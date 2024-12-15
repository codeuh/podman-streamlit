import streamlit as st

connections = {
    "Local User Podman Socket": "unix:///run/user/1000/podman/podman.sock"
}

def show_sidebar_socket_selector():
    """
    Show a selectbox in the sidebar to choose a Podman API connection.

    This function provides an interface for users to select from available
    connections and updates the session state accordingly. If the selected
    URI changes, it triggers a rerun of the Streamlit app.

    Returns:
        str: The URI of the selected Podman API connection.
    """
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
    """
    Display Podman information in the sidebar.

    This function retrieves version information from the provided client and 
    displays it as metrics in the Streamlit app's sidebar. The displayed 
    information includes the release version, compatible API version, OS, 
    architecture, and Go version used by Podman.

    Args:
        client (PodmanClient): A client object with a `version()` method to retrieve Podman version information.
    """
    st.sidebar.header("Podman Information")

    version = client.version()
    st.sidebar.metric("Release", version["Version"])
    st.sidebar.metric("Compatible API", version["ApiVersion"])
    st.sidebar.metric("OS", version["Components"][0]["Details"]["Os"])
    st.sidebar.metric("Arch", version["Arch"])
    st.sidebar.metric("Go Version", version["GoVersion"])