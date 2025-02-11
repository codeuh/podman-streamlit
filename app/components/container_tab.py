import streamlit as st
import pandas as pd
from utils import container_utils

def show(client):
    """
    Displays a tab for managing Podman containers.

    This function generates a Streamlit interface to display and manage Podman containers.
    It provides buttons for starting, pausing, stopping, and removing containers,
    as well as a data editor to select specific containers for these actions.

    Parameters:
        client (PodmanClient): The client object used to interact with the containers.

    Returns:
        None
    """
    st.header("📦 Podman Containers")
    container_data = container_utils.get(client)

    df_containers = pd.DataFrame(container_data)         

    containerCols = st.columns((1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))

    with containerCols[0]:
        inspect_all = st.button("🔍", help="Inspect Selected Containers")

    with containerCols[1]:
        show_links = st.button("🌐", help="Show Selected Links")

    with containerCols[2]:
        log_all = st.button("📄", help="Show Selected Logs")
    
    with containerCols[3]:
        generate_quadlet = st.button("📜", help="Generate Selected Quadlets")

    with containerCols[4]:
        container_exec = st.button("⚙️", help="Execute in Container")

    with containerCols[5]:
        start_all = st.button("▶️", help="Start Selected Containers")

    with containerCols[6]:
        pause_all = st.button("⏸️", help="Pause Selected Containers")

    with containerCols[7]:
        stop_all = st.button("⏹️", help="Stop Selected Containers")

    with containerCols[8]:
        remove_all = st.button("🗑️", help="Remove Selected Containers")

    with containerCols[9]:
        if st.button("✂️", help="Prune All Containers"):
            client.containers.prune()  
            st.rerun()
    
    with containerCols[10]:
         refresh_all = st.button("🔄", help= "Refresh All Containers")  

    edited_containers_df = st.data_editor(df_containers, 
                    hide_index=True,
                    disabled=("Status","Name","ID","Image","Ports","Created"), 
                    column_config={
                        "Selected": st.column_config.CheckboxColumn(
                            "",
                            help="Select containers for actions"
                        ),
                    },
                    column_order=["Selected", "Name", "Status", "Image", "Ports", "Created"],
                    use_container_width=True)

    selected_containers = edited_containers_df[edited_containers_df['Selected']]

    if inspect_all and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            st.write(container.attrs)

    if show_links and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            ports = container.attrs['NetworkSettings']['Ports']
            if ports:
                for port, mappings in ports.items():
                    if mappings:
                        host_port = mappings[0]['HostPort']
                        url = f"http://localhost:{host_port}"
                        st.write(f"{container.name}: {url}")

    if log_all and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            logs = container.logs(stream=False,stdout=True, stderr=True,)

            st.subheader(f"{row["Name"]}'s Logs")

            log_placeholder = st.empty()
            log_lines = []

            for log_line in logs:
                decoded_log_line = log_line.decode('utf-8').strip()
                if decoded_log_line:
                    log_lines.append(decoded_log_line)
            log_placeholder.code("\n".join(log_lines),"log")

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
        
    if refresh_all:
        st.rerun()

    if generate_quadlet and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container_utils.run_podlet(client, row["Name"], row['RunCommand'])

    if container_exec:
        container_utils.execute(df_containers, selected_containers['Name'].tolist())

    if "execute_outputs" in st.session_state:
        with st.expander("Execution Outputs", True):
            if st.button("Clear Outputs"):
                del st.session_state["execute_outputs"]
                st.rerun()
            if st.session_state.execute_outputs:
                st.subheader("Command executed:")
                st.code(st.session_state.execute_outputs[0]['command'], "bash")
            for output in st.session_state.execute_outputs:
                st.subheader(f"{output['container']}'s output:")
                st.code(output['output'], "text")