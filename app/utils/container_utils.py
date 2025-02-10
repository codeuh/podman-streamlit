import streamlit as st
from utils.status_icons import *
from dateutil import parser 
from tzlocal import get_localzone

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
            - "Ports": A string describing the ports exposed by the container.- "Ports": A string describing the ports exposed by the container.
            - "Created": The creation time of the container, formatted as a string.
    Notes:
        This function also updates the `st.session_state.container_objects` dictionary, which maps container IDs to their corresponding Podman client objects.
    """
    containers = client.containers.list(all=True)
    
    st.session_state.container_objects = {}
    container_data = []
    
    if containers:
        my_timezone = get_localzone() 
        for container in containers:
            container.reload()
            created_timestamp = container.attrs["Created"]
            created_time = parser.isoparse(created_timestamp).astimezone(my_timezone)
            formatted_ports = ", ".join(
                f"{value.get('HostPort', 'N/A')} -> {key}"
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
                "Created": created_time,
            })
            
            st.session_state.container_objects[container.short_id] = container
    return container_data