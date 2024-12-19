import streamlit as st
import pandas as pd

def show_network_tab(client):
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

        for network in networks:
            created_timestamp = network.attrs.get("created", 0)

            network_data.append({
                "Selected": False,
                "Name": network.name,
                "ID": network.short_id,
                "Driver": network.attrs["driver"],
                "Created": created_timestamp,
            })

        df_networks = pd.DataFrame(network_data)

        networkCols = st.columns((1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))

        with networkCols[0]:
            inspect_all = st.button("🔍", help="Inspect Selected Networks")

        with networkCols[1]:
            remove_all = st.button("🗑️", help="Remove Selected Networks")

        with networkCols[2]:
            refresh_all = st.button("🔄", help="Refresh All Networks")

        edited_networks_df = st.data_editor(df_networks, 
                    hide_index=True,
                    disabled=("Name","Driver","Created"), 
                    column_config={
                        "Selected": st.column_config.CheckboxColumn(
                            "",
                            help="Select networks for actions"
                        )
                    },
                    use_container_width=True)

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