import streamlit as st
import pandas as pd
from utils.container_utils import get_containers

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
    st.header("🛳️ Podman Containers")
    container_data = get_containers(client)

    df_containers = pd.DataFrame(container_data)

    containerCols = st.columns((1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))

    with containerCols[0]:
        start_all = st.button("▶️", help="Start Container")

    with containerCols[1]:
        pause_all = st.button("⏸️", help="Pause Container")

    with containerCols[2]:
        stop_all = st.button("⏹️", help="Stop Container")

    with containerCols[3]:
        remove_all = st.button("🗑️", help="Remove Container")

    with containerCols[4]:
        if st.button("✂️", help="Prune Containers"):
            client.containers.prune()  
            st.rerun()

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