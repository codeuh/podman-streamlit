import streamlit as st
from podman import PodmanClient
import pandas as pd
from datetime import datetime

# App Title and Description
st.set_page_config(page_title="Podman Manager", page_icon="🦭", layout="wide")
st.title("🦭 Podman Manager🦭")
st.markdown(
    """
    This app displays **Podman container information** in an organized and interactive way.
    """
)

# Define the Podman socket URI
uri = "unix:///run/user/1000/podman/podman.sock"

# Fetch and display Podman version details
st.sidebar.header("Podman Information")
try:
    with PodmanClient(base_url=uri) as client:
        version = client.version()
        st.sidebar.metric("Release", version["Version"])
        st.sidebar.metric("Compatible API", version["ApiVersion"])
        st.sidebar.metric("Podman API", version["Components"][0]["Details"]["APIVersion"])

        # Display containers in a table
        st.header("🛳️ Podman Containers")
        containers = client.containers.list()

        if containers:
            # Prepare data for the table
            container_data = []
            for container in containers:
                container.reload()
                container_data.append({
                    "Name": container.name,
                    "ID": container.id[:12],
                    "Status": container.status,
                    "Image": container.image
                })

            # Convert to a Pandas DataFrame
            df_containers = pd.DataFrame(container_data)

            # Display the DataFrame as a table
            st.dataframe(df_containers, use_container_width=True)
        else:
            st.info("No containers found.")

        # Display images in a table
        st.header("📦 Podman Images")
        images = client.images.list()

        if images:
            # Prepare data for the table
            image_data = []
            for image in images:
                readable_time = datetime.utcfromtimestamp(image.attrs.get("Created", 0)).strftime('%Y-%m-%d %H:%M:%S')
                image_data.append({
                    "Tags": ', '.join(image.tags) if image.tags else "None",
                    "ID": image.short_id,
                    "Size (MB)": round(image.attrs.get("Size", 0) / 1024 / 1024, 2),
                    "Created": readable_time,
                })

            # Convert to a Pandas DataFrame
            df_images = pd.DataFrame(image_data)

            # Display the DataFrame as a table
            st.dataframe(df_images, use_container_width=True)
        else:
            st.info("No images found.")

        # Display resource usage
        st.header("📊 Podman Resource Usage")
        resource_data = client.df()
        st.json(resource_data)
except Exception as e:
    st.error(f"Error connecting to Podman: {e}")
