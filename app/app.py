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

st.set_page_config(page_title="Podman Manager 🦭", page_icon="🦭", layout="wide")
st.title("🦭 Podman Manager 🦭")
st.markdown(
    """
    This app displays **Podman container information** in an organized and interactive way.
    """
)

uri = "unix:///run/user/1000/podman/podman.sock"

st.sidebar.header("Podman Information")
try:
    with PodmanClient(base_url=uri) as client:
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
                    status_icon = status_icons.get(container.status.lower(), "❓")
                    container_data.append({
                        "Status": f"{status_icon} {container.status}",
                        "Name": container.name,
                        "ID": container.short_id,
                        "Image": container.image,
                        "Ports": container.ports,
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
                        "Tags": ', '.join(image.tags) if image.tags else "None",
                        "ID": image.short_id,
                        "Size (MB)": round(image.attrs.get("Size", 0) / 1024 / 1024, 2),
                        "Created": readable_time,
                    })

                df_images = pd.DataFrame(image_data)

                st.dataframe(df_images, hide_index=True, use_container_width=True)
            else:
                st.info("No images found.")

        with secretTab:
            secrets_list = get_cached_secrets()
            
            createCol, deleteCol = st.columns(2)

            with createCol:
                nameCol, dataCol = st.columns(2)
                with nameCol:
                    secret_name = st.text_input("Enter your secret name:")
                with dataCol:
                    secret_data = st.text_input("Enter your secret data:", type="password")
                if st.button("Create Secret"):
                    if not secret_name or not secret_data:
                        st.error("Please provide both a secret name and data.")
                    else:
                        new_secret = create_secret(secret_name, secret_data)
                        st.success(f"Created Secret {new_secret.name} successfully!")
                        refresh_cached_secrets()  

            with deleteCol:
                secrets_list = get_cached_secrets()
                secret_names = {secret["Name"]: secret["ID"] for secret in secrets_list}  
                secret_to_delete = st.selectbox("Select a secret to delete:", options=list(secret_names.keys()))
                if st.button("Delete Secret"):
                    secret_id = secret_names.get(secret_to_delete)
                    try:
                        delete_secret(secret_id)
                        st.success(f"Secret '{secret_to_delete}' deleted successfully!")
                        refresh_cached_secrets()  
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
