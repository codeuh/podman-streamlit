import streamlit as st
from podman import PodmanClient
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

@st.cache_data
def get_cached_secrets():
    secrets_list = list_secrets()
    return [{"Name": secret.name, "ID": secret.id} for secret in secrets_list]

def refresh_cached_secrets():
    st.cache_data.clear()
    return get_cached_secrets()

def list_secrets():
    return client.secrets.list()

def create_secret(secret_name, data):
    secret = client.secrets.create(name=secret_name, 
                                  data=data)
    return secret

def delete_secret(secret_id):
    try:
        client.secrets.remove(secret_id)
        print(f"Secret {secret_id} deleted successfully.")
    except Exception as e:
        print(str(e))

@st.cache_data
def secret_exists(secret_name):
    """Check if a secret with the given name already exists."""
    secrets = get_cached_secrets()  # Retrieve the cached secrets
    return any(secret["Name"] == secret_name for secret in secrets)

st.set_page_config(page_title="Podman Streamlit 🦭", page_icon="🦭", layout="wide")
st.title("🦭 Podman Streamlit 🦭")
st.markdown(
    """
    This app displays **Podman container information** in an organized and interactive way.
    """
)

connections = {
    "Local User Podman Socket": "unix:///run/user/1000/podman/podman.sock"
}

try:
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

    st.sidebar.header("Podman Information")

    with PodmanClient(base_url=selected_uri, identity="~/.ssh/id_ed25519") as client:
        version = client.version()
        st.sidebar.metric("Release", version["Version"])
        st.sidebar.metric("Compatible API", version["ApiVersion"])
        st.sidebar.metric("OS", version["Components"][0]["Details"]["Os"])
        st.sidebar.metric("Arch", version["Arch"])
        st.sidebar.metric("Go Version", version["GoVersion"])

        containerTab, imageTab, secretTab = st.tabs(["Containers", "Images", "Secrets"])

        with containerTab:
            st.header("🛳️ Podman Containers")
            containers = client.containers.list()

            if containers:
                container_data = []
                status_icons = {
                    "running": "🟢",
                    "exited": "🔴",
                    "paused": "⏸️",
                    "created": "💡"
                }

                for container in containers:
                    container.reload()

                    formatted_ports = ", ".join(
                        f"{key} -> HostIp: {value['HostIp']}, HostPort: {value['HostPort']}"
                        for key, values in container.ports.items()
                        if values
                        for value in values
                    )

                    status_icon = status_icons.get(container.status.lower(), "❓")
                    container_data.append({
                        "Status": f"{status_icon} {container.status}",
                        "Name": container.name,
                        "ID": container.short_id,
                        "Image": container.image.tags,
                        "Ports": formatted_ports,
                    })

                df_containers = pd.DataFrame(container_data)

                st.dataframe(df_containers, hide_index=True, use_container_width=True)
            else:
                st.info("No containers found.")

        with imageTab:
            st.header("📦 Podman Images")
            images = client.images.list()

            if images:
                image_data = []
                local_timezone = datetime.now().astimezone().tzinfo
                now = datetime.now(local_timezone)
                for image in images:
                    created_timestamp = image.attrs.get("Created", 0)
                    created_time = datetime.fromtimestamp(created_timestamp, local_timezone)
                    relative_time = relativedelta(now, created_time)

                    if relative_time.years:
                        readable_time = f"{relative_time.years} years, {relative_time.months} months, {relative_time.days} days ago"
                    elif relative_time.months:
                        readable_time = f"{relative_time.months} months, {relative_time.days} days ago"
                    elif relative_time.days:
                        readable_time = f"{relative_time.days} days ago"
                    elif relative_time.hours:
                        readable_time = f"{relative_time.hours} hours, {relative_time.minutes} minutes ago"
                    else:
                        readable_time = f"{relative_time.minutes} minutes ago"

                    image_data.append({
                        #"Tags": ', '.join(image.tags) if image.tags else "None",
                        "Tags": image.tags,
                        "ID": image.short_id,
                        "Size (MB)": round(image.attrs.get("Size", 0) / 1024 / 1024, 2),
                        "Created": readable_time,
                    })

                df_images = pd.DataFrame(image_data)

                st.dataframe(df_images, hide_index=True, use_container_width=True)
            else:
                st.info("No images found.")

        with secretTab:
            st.header("🔐 Podman Secrets")
            secrets_list = get_cached_secrets()
            
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
                        if secret_exists(secret_name): 
                            st.warning(f"A secret with the name '{secret_name}' already exists.")
                        else:
                            create_secret(secret_name, secret_data)  
                            refresh_cached_secrets()  
                            st.rerun()

            with deleteCol:
                secrets_list = get_cached_secrets()
                secret_names = {secret["Name"]: secret["ID"] for secret in secrets_list}  
                secret_to_delete = st.selectbox("Delete secret:", options=list(secret_names.keys()))
                if st.button("Delete Secret"):
                    secret_id = secret_names.get(secret_to_delete)
                    try:
                        delete_secret(secret_id)
                        refresh_cached_secrets()  
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting secret: {str(e)}")

            if secrets_list:
                st.dataframe(secrets_list, use_container_width=True)
            else:
                st.info("No secrets found.")
                
    with st.expander("Resource Usage Details"):
        resource_data = client.df()
        st.json(resource_data)

except Exception as e:
    st.exception(e)
