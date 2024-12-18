import streamlit as st
import pandas as pd
from utils.container_utils import get_containers

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
    if st.button("Run"):
        output = container.exec_run(command,stderr=True, stdout=True)  
        try:
            decoded_output = output[1].decode('utf-8').strip()
        except UnicodeDecodeError:
            decoded_output = output[1].decode('utf-8', errors='replace').strip()
        cleaned_output = ''.join(char for char in decoded_output if char.isprintable() or char.isspace())
        st.session_state.execute = {"container": container, "command": command, "output": cleaned_output}
        st.rerun()

def show_container_tab(client):
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
    container_data = get_containers(client)

    df_containers = pd.DataFrame(container_data)         

    containerCols = st.columns((1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))

    with containerCols[0]:
        inspect_all = st.button("🔍", help="Inspect Container")

    with containerCols[1]:
        log_all = st.button("📜", help="Container Logs")

    with containerCols[2]:
        start_all = st.button("▶️", help="Start Container")

    with containerCols[3]:
        pause_all = st.button("⏸️", help="Pause Container")

    with containerCols[4]:
        stop_all = st.button("⏹️", help="Stop Container")

    with containerCols[5]:
        remove_all = st.button("🗑️", help="Remove Container")

    with containerCols[6]:
        if st.button("✂️", help="Prune Containers"):
            client.containers.prune()  
            st.rerun()
    
    with containerCols[7]:
         refresh_all = st.button("🔄", help= "Refresh Container")  

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

    if inspect_all and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            st.write(container.attrs)

    if log_all and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            logs = container.logs(stream=False,stdout=True, stderr=True,)

            st.subheader(f"Logs for container: {row['Name']}")

            log_placeholder = st.empty()
            log_lines = []

            for log_line in logs:
                decoded_log_line = log_line.decode('utf-8')
                if decoded_log_line.strip():
                    log_lines.append(decoded_log_line)
            log_placeholder.code("\n".join(log_lines))

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


    with st.expander("Avanced Container Tools"):
        executeTab,otherTab = st.tabs(["Execute","Other"])
        
        with executeTab:
            executeCols = st.columns(2)
            with executeCols[0]:
                container_exec = st.button("Execute Command in Container")
            with executeCols[1]:
                container_exec_clear = st.button("Clear Command and Output")
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