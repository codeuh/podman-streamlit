import streamlit as st
from podman import PodmanClient
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Podman Manager", page_icon="🦭", layout="wide")
st.title("🦭 Podman Manager🦭")
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

        containerTab, imageTab = st.tabs(["Containers", "Images"])
        with containerTab:
            st.header("🛳️ Podman Containers")
            containers = client.containers.list()

            if containers:
                container_data = []
                for container in containers:
                    container.reload()
                    container_data.append({
                        "Name": container.name,
                        "ID": container.id[:12],
                        "Status": container.status,
                        "Image": container.image
                    })

                df_containers = pd.DataFrame(container_data)

                st.dataframe(df_containers,column_config={
                        "Name": st.column_config.TextColumn("Container Name"),
                        "ID": st.column_config.TextColumn("Container ID"),
                        "Status": st.column_config.TextColumn("Status"),
                        "Image": st.column_config.TextColumn("Image Name"),
                    }, hide_index=True, use_container_width=True)
            else:
                st.info("No containers found.")

        with imageTab:
            st.header("📦 Podman Images")
            images = client.images.list()

            if images:
                image_data = []
                for image in images:
                    readable_time = datetime.utcfromtimestamp(image.attrs.get("Created", 0)).strftime('%Y-%m-%d %H:%M:%S')
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

        with st.expander("Resource Usage Details"):
            resource_data = client.df()
            st.json(resource_data)
except Exception as e:
    st.exception(e)
