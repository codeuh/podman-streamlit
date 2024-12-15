import streamlit as st

status_icons = {
                    "running": "🟢",
                    "stopped": "🛑",
                    "exited": "🔴",
                    "paused": "⏸️",
                    "created": "💡"
                }

def get_containers(client):
    """
    Retrieves a list of Podman containers and their associated metadata.

    Args:
        client (PodmanClient): A client object used to interact with the Podman socket.

    Returns:
        A list of dictionaries, where each dictionary represents a container and contains the following keys:
            - "Selected": A boolean indicating whether the container is selected.
            - "Status": The status of the container, prefixed with an icon representing its state.
            - "Name": The name of the container.
            - "ID": The short ID of the container.
            - "Image": The tags associated with the container's image.
            - "Ports": A string describing the ports exposed by the container.

    Notes:
        This function also updates the `st.session_state.container_objects` dictionary, which maps container IDs to their corresponding Podman client objects.
    """
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