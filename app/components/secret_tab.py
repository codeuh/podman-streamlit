import streamlit as st
from utils import secret_utils

def show(client):
    """
    Displays a tab for managing Podman secrets.

    This function creates a Streamlit interface with options to create and delete secrets.
    It fetches the list of existing secrets from the client and displays them in a dataframe.
    
    Args:
        client (PodmanClient): The client object used to interact with the Podman API.

    Returns:
        None
    """
    st.header("🔐 Podman Secrets")
    secrets_list = secret_utils.get_cached_secrets(client)

    createCol, deleteCol = st.columns(2)

    with createCol:
        nameCol, dataCol = st.columns(2)
        with nameCol:
            secret_name = st.text_input("Secret name:", key="secret_name_input")
        with dataCol:
            secret_data = st.text_input("Secret data:", type="password", key="secret_data_input")

        if st.button("Create Secret"):
            if not secret_name or not secret_data:
                st.error("Please provide both a secret name and data.")
            else:
                if secret_utils.secret_exists(client, secret_name):
                    st.warning(f"A secret with the name '{secret_name}' already exists.")
                else:
                    secret_utils.create_secret(client,secret_name, secret_data)
                    st.rerun()

    with deleteCol:
        secret_names = {secret["Name"]: secret["ID"] for secret in secrets_list}
        secret_to_delete = st.selectbox("Delete secret:", options=list(secret_names.keys()))
        if st.button("Delete Secret"):
            secret_id = secret_names.get(secret_to_delete)
            try:
                secret_utils.delete_secret(client, secret_id)
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting secret: {str(e)}")

    if secrets_list:
        st.dataframe(secrets_list, use_container_width=True)
    else:
        st.info("No secrets found.")