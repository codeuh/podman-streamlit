import streamlit as st
import pandas as pd
from utils import container_utils
from . import container_buttons

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

    inspect          = container_buttons.show_inspect(containerCols[0])
    show_links       = container_buttons.show_links(containerCols[1])
    logs             = container_buttons.show_logs(containerCols[2])
    generate_quadlet = container_buttons.show_generate_quadlet(containerCols[3])
    container_exec   = container_buttons.show_exec(containerCols[4])
    start            = container_buttons.show_start(containerCols[5])
    pause            = container_buttons.show_pause(containerCols[6])
    stop             = container_buttons.show_stop(containerCols[7])
    remove           = container_buttons.show_remove(containerCols[8])
    prune            = container_buttons.show_prune(containerCols[9])
    refresh          = container_buttons.show_refresh(containerCols[10])

    edited_containers_df = st.data_editor(
        df_containers, 
        hide_index=True,
        disabled=("Status", "Name", "ID", "Image", "Ports", "Created"), 
        column_config={
            "Selected": st.column_config.CheckboxColumn(
                "",
                help="Select containers for actions"
            ),
        },
        column_order=["Selected", "Name","ID", "Status", "Image", "Ports", "Created"],
        use_container_width=True
    )

    selected_containers = edited_containers_df[edited_containers_df['Selected']]

    container_buttons.handle_inspect(inspect, selected_containers)
    container_buttons.handle_links(show_links, selected_containers)
    container_buttons.handle_logs(logs, selected_containers)
    container_buttons.handle_generate_quadlet(generate_quadlet, selected_containers, client)
    container_buttons.handle_exec(container_exec, df_containers, selected_containers)
    container_buttons.handle_start(start, selected_containers)
    container_buttons.handle_pause(pause, selected_containers)
    container_buttons.handle_stop(stop, selected_containers)
    container_buttons.handle_remove(remove, selected_containers)
    container_buttons.handle_prune(prune, client)
    container_buttons.handle_refresh(refresh, client)        