import streamlit as st
from podman import PodmanClient
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import altair as alt

status_icons = {
                    "running": "🟢",
                    "stopped": "🛑",
                    "exited": "🔴",
                    "paused": "⏸️",
                    "created": "💡"
                }

def get_containers():
    containers = client.containers.list(all=True)
    
    st.session_state.container_objects = {}
    container_data = []
    
    if containers:
        for container in containers:
            container.reload()
            
            formatted_ports = ", ".join(
                f"{key} -> HostIp: {value.get('HostIp', 'N/A')}, HostPort: {value.get('HostPort', 'N/A')}"
                for key, values in container.ports.items()
                if values
                for value in values
            ) if container.ports else "No ports"

            status_icon = status_icons.get(container.status.lower(), "❓")
            
            container_data.append({
                "Selected": False,
                "Status": f"{status_icon} {container.status}",
                "Name": container.name,
                "ID": container.short_id,
                "Image": container.image.tags,
                "Ports": formatted_ports,
            })
            
            st.session_state.container_objects[container.short_id] = container
    return container_data

def get_cached_secrets():
    secrets_list = list_secrets()
    return [{"Name": secret.name, "ID": secret.id} for secret in secrets_list]

def refresh_cached_secrets():
    st.cache_data.clear()
    return get_cached_secrets()

def list_secrets():
    return client.secrets.list()

def create_secret(secret_name, data):
    secret = client.secrets.create(name=secret_name, data=data)
    return secret

def delete_secret(secret_id):
    try:
        client.secrets.remove(secret_id)
        print(f"Secret {secret_id} deleted successfully.")
    except Exception as e:
        print(str(e))

def secret_exists(secret_name):
    secrets = get_cached_secrets()
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
            container_data = get_containers()

            df_containers = pd.DataFrame(container_data)

            containerCols = st.columns((1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))

            with containerCols[0]:
                start_all = st.button("▶️", help="Start Container")

            with containerCols[1]:
                pause_all = st.button("⏸️", help="Pause Container")

            with containerCols[2]:
                stop_all = st.button("⏹️", help="Stop Container")

            with containerCols[3]:
                remove_all = st.button("🗑️", help="Remove Container")
            
            with containerCols[4]:
               if st.button("✂️", help="Prune Containers"):
                   client.containers.prune()  
                   st.rerun()

            edited_containers_df = st.data_editor(df_containers, 
                            hide_index=True,
                            disabled=("Status","Name","ID","Image","Ports"), 
                            column_config={
                                "Selected": st.column_config.CheckboxColumn(
                                    "",
                                    help="Select containers for actions"
                                )
                            },
                            use_container_width=True)
            
            selected_containers = edited_containers_df[edited_containers_df['Selected']]

            if start_all and not selected_containers.empty:
                for _, row in selected_containers.iterrows():
                    container = st.session_state.container_objects[row['ID']]
                    if container.status == "paused":
                        container.unpause()
                    elif container.status == "exited":
                        container.start(force=True)
                st.rerun()

            if pause_all and not selected_containers.empty:
                for _, row in selected_containers.iterrows():
                    container = st.session_state.container_objects[row['ID']]
                    if container.status == "running":
                        container.pause()
                st.rerun()

            if stop_all and not selected_containers.empty:
                for _, row in selected_containers.iterrows():
                    container = st.session_state.container_objects[row['ID']]
                    if container.status != "paused":
                        container.stop()
                    else:
                        container.kill()
                st.rerun()

            if remove_all and not selected_containers.empty:
                for _, row in selected_containers.iterrows():
                    container = st.session_state.container_objects[row['ID']]
                    container.remove(force=True)
                st.rerun()

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

        st.subheader("Containers")
        container_data = pd.DataFrame(resource_data["Containers"])
        container_data["Size_MB"] = container_data["Size"] / (1024 * 1024)

        container_chart = alt.Chart(container_data).mark_bar().encode(
            y=alt.Y("Names:N", sort="-x", title="Container Names"),
            x=alt.X("Size_MB:Q", title="Size (MB)"),
            color=alt.Color("Status:N", title="Status"),
            tooltip=["Names", "Status", "Size_MB"]
        ).properties(height=300)
        st.altair_chart(container_chart, use_container_width=True)

        st.subheader("Images")
        image_data = pd.DataFrame(resource_data["Images"])
        image_data["Size_MB"] = image_data["Size"] / (1024 * 1024)

        image_chart = alt.Chart(image_data).mark_bar().encode(
            y=alt.Y("Repository:N", sort="-x", title="Repository"),
            x=alt.X("Size_MB:Q", title="Size (MB)"),
            color=alt.Color("Tag:N", title="Tag"),
            tooltip=["Repository", "Tag", "Size_MB"]
        ).properties(height=300)
        st.altair_chart(image_chart, use_container_width=True)

        st.subheader("Volumes")
        volume_data = pd.DataFrame(resource_data["Volumes"])
        volume_data["Size_MB"] = volume_data["Size"] / (1024 * 1024)
        volume_data["ReclaimableSize_MB"] = volume_data["ReclaimableSize"] / (1024 * 1024)

        volume_chart = alt.Chart(volume_data).mark_bar().encode(
            y=alt.Y("VolumeName:N", sort="-x", title="Volume Name"),
            x=alt.X("Size_MB:Q", title="Size (MB)"),
            color=alt.Color("Links:Q", title="Links"),
            tooltip=["VolumeName", "Size_MB", "ReclaimableSize_MB", "Links"]
        ).properties(height=300)
        st.altair_chart(volume_chart, use_container_width=True)

        reclaimable_space = volume_data[volume_data["ReclaimableSize_MB"] > 0]
        st.write("Volumes with reclaimable space:")
        reclaimable_chart = alt.Chart(reclaimable_space).mark_bar().encode(
            y=alt.Y("VolumeName:N", sort="-x", title="Volume Name"),
            x=alt.X("ReclaimableSize_MB:Q", title="Reclaimable Size (MB)"),
            color=alt.Color("Links:Q", title="Links"),
            tooltip=["VolumeName", "ReclaimableSize_MB", "Links"]
        ).properties(height=300)
        st.altair_chart(reclaimable_chart, use_container_width=True)

    # not very efficent
    time.sleep(2)  
    st.rerun()

except Exception as e:
    st.exception(e)
