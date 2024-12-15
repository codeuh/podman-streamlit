import streamlit as st

status_icons = {
                    "running": "🟢",
                    "stopped": "🛑",
                    "exited": "🔴",
                    "paused": "⏸️",
                    "created": "💡"
                }

def get_containers(client):
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