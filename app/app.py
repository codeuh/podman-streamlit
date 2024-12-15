import streamlit as st
from podman import PodmanClient
from components.header import show_header
from components.sidbar import show_sidebar_details, show_sidebar_uri_selector
from components.container_tab import show_container_tab
from components.pod_tab import show_pod_tab
from components.image_tab import show_image_tab
from components.volume_tab import show_volume_tab
from components.network_tab import show_network_tab
from components.secret_tab import show_secret_tab
from components.usage_details import show_usage_details

show_header()

try:
    selected_uri = show_sidebar_uri_selector()

    with PodmanClient(base_url=selected_uri, identity="~/.ssh/id_ed25519") as client:

        show_sidebar_details(client)

        containerTab, podTab, imageTab, volumeTab, networkTab, secretTab = st.tabs(["Containers", "Pods", "Images", "Volumes", "Networks","Secrets"])

        with containerTab:
            show_container_tab(client)

        with podTab:
            show_pod_tab(client)

        with imageTab:
            show_image_tab(client)
        
        with volumeTab:
            show_volume_tab(client)

        with networkTab:
            show_network_tab(client)

        with secretTab:
            show_secret_tab(client)  
                
    with st.expander("Resource Usage Details"):
        show_usage_details(client)

except Exception as e:
    st.exception(e)