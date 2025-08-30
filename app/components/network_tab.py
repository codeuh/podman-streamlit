import streamlit as st
import pandas as pd
from dateutil import parser 
from tzlocal import get_localzone

def show(client):
    """
    Displays a tab in Streamlit that shows information about Podman networks.

    This function connects to the client, retrieves a list of available networks,
    and displays their details, including names, drivers, and creation times.
    
    Args:
        client (PodmanClient): A client object used to connect to the container runtime.
        
    Returns:
        None
    """
    st.header("🌐 Podman Networks")
    networks = client.networks.list()
    if networks:
        network_data = []
        my_timezone = get_localzone()
        for network in networks:
            created_timestamp = network.attrs["created"]
            created_time = parser.isoparse(created_timestamp).astimezone(my_timezone)
            network_data.append({
                "Selected": False,
                "Name": network.name,
                "ID": network.short_id,
                "Driver": network.attrs["driver"],
                "Created": created_time,
            })

        df_networks = pd.DataFrame(network_data)

        action = st.selectbox(
            "Network Actions",
            [
                "Select action...",
                "🔍 Inspect",
                "🗑️ Remove",
                "🔄 Refresh"
            ]
        )

        # Convert dropdown selection to button clicks
        inspect_all = action == "🔍 Inspect"
        remove_all = action == "🗑️ Remove"
        refresh_all = action == "🔄 Refresh"

        edited_networks_df = st.data_editor(df_networks, 
                    hide_index=True,
                    disabled=("Name","Driver","Created"), 
                    column_config={
                        "Selected": st.column_config.CheckboxColumn(
                            "",
                            help="Select networks for actions"
                        )
                    },
                    width="stretch")

        selected_networks = edited_networks_df[edited_networks_df['Selected']]

        if inspect_all and not selected_networks.empty:
            for _, row in selected_networks.iterrows():
                network_name = row['Name']
                network = client.networks.get(network_name)
                st.write(network.attrs)

        if remove_all and not selected_networks.empty:
            for _, row in selected_networks.iterrows():
                network_name = row['Name']
                network = client.networks.get(network_name)
                network.remove()
            st.rerun()

        if refresh_all:
            st.rerun()
    else:
        st.info("No networks found.")