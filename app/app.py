import streamlit as st
from podman import PodmanClient
from components import (
    header,
    sidebar,
    container_tab,
    pod_tab,
    image_tab,
    volume_tab,
    network_tab,
    secret_tab,
    usage_details
)

def main():
    st.set_page_config(page_title="Podman Streamlit 🦭", page_icon="🦭", layout="wide")
    
    header.show()

    try:
        selected_uri = sidebar.show_uri_selector()

        with PodmanClient(base_url=selected_uri, identity="~/.ssh/id_ed25519") as client:

            sidebar.show_details(client)

            containerTab, podTab, imageTab, volumeTab, networkTab, secretTab = st.tabs(
                ["Containers", "Pods", "Images", "Volumes", "Networks", "Secrets"]
            )

            with containerTab:
                container_tab.show(client)

            with podTab:
                pod_tab.show(client)

            with imageTab:
                image_tab.show(client)
            
            with volumeTab:
                volume_tab.show(client)

            with networkTab:
                network_tab.show(client)

            with secretTab:
                secret_tab.show(client)  
                    
        with st.expander("Resource Usage Details"):
            usage_details.show(client)

    except Exception as e:
        st.exception(e)

if __name__ == "__main__":
    main()