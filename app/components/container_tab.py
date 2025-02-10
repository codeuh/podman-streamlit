import streamlit as st
import pandas as pd
from utils import container_utils

@st.dialog("Execute Container")
def execute(item):
    """
    Execute a command in a selected container.

    This function creates a dialog for executing a command in a Podman container.
    It allows the user to select a container, input a command, and run it.
    The output of the command is then displayed in the Streamlit app.

    Args:
        item: An object containing information about the available containers.

    Returns:
        None
    """
    selected_name = st.selectbox("Select a Container",options=item.Name)
    command = st.text_input("Execute command:")
    container_id = next((c for c in st.session_state.container_objects.keys() if st.session_state.container_objects[c].name == selected_name), None)
    container = st.session_state.container_objects[container_id]
    if st.button("Execute"):
        with st.spinner("Executing..."):
            output = container.exec_run(command,stderr=True, stdout=True)  
            try:
                decoded_output = output[1].decode('utf-8').strip()
            except UnicodeDecodeError:
                decoded_output = output[1].decode('utf-8', errors='replace').strip()
            cleaned_output = ''.join(char for char in decoded_output if char.isprintable() or char.isspace())
            st.session_state.execute = {"container": container, "command": command, "output": cleaned_output}
            st.rerun()

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

    containerCols = st.columns((1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))

    with containerCols[0]:
        inspect_all = st.button("🔍", help="Inspect Selected Containers")

    with containerCols[1]:
        show_links = st.button("🌐", help="Show Selected Links")

    with containerCols[2]:
        log_all = st.button("📄", help="Show Selected Logs")
    
    with containerCols[3]:
        generate_quadlet = st.button("📜", help="Generate Selected Quadlets")

    with containerCols[4]:
        start_all = st.button("▶️", help="Start Selected Containers")

    with containerCols[5]:
        pause_all = st.button("⏸️", help="Pause Selected Containers")

    with containerCols[6]:
        stop_all = st.button("⏹️", help="Stop Selected Containers")

    with containerCols[7]:
        remove_all = st.button("🗑️", help="Remove Selected Containers")

    with containerCols[8]:
        if st.button("✂️", help="Prune All Containers"):
            client.containers.prune()  
            st.rerun()
    
    with containerCols[9]:
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
                        st.write(f"Url for container {container.name}: {url}")

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

    with st.expander("Avanced Container Tools"):
        executeTab,otherTab = st.tabs(["Execute","Other"])
        
        with executeTab:
            executeCols = st.columns(2)
            with executeCols[0]:
                container_exec = st.button("Execute in Container")
            with executeCols[1]:
                container_exec_clear = st.button("Clear Output",key="conatiner-clear-output")
            if container_exec:
                execute(df_containers)

            if container_exec_clear:
                if "execute" in st.session_state:
                    del st.session_state["execute"]
            
            if "execute" in st.session_state:
                st.write(f"command ran in container {st.session_state.execute["container"].name}")
                st.code(st.session_state.execute["command"])
                st.write("output:")
                st.code(st.session_state.execute["output"])