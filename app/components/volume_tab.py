import streamlit as st
import pandas as pd

def show_volume_tab(client):
    """
    Displays a tab in Streamlit that shows information about Podman volumes.

    This function connects to the client, retrieves a list of available volumes,
    and displays their details, including names and creation times.
    
    Args:
        client (PodmanClient): A client object used to connect to the container runtime.
        
    Returns:
        None
    """
    st.header("💽 Podman Volumes")
    volumes = client.volumes.list()
    if volumes:
        volume_data = []

        for volume in volumes:
            created_timestamp = volume.attrs.get("CreatedAt", 0)

            volume_data.append({
                "Selected": False,
                "Name": volume.short_id,
                "Created": created_timestamp,
            })

        df_volumes = pd.DataFrame(volume_data)

        volumeCols = st.columns((1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))

        with volumeCols[0]:
            inspect_all = st.button("🔍", help="Inspect Selected Volumes")

        with volumeCols[1]:
            remove_all = st.button("🗑️", help="Remove Selected Volumes")

        with volumeCols[2]:
            prune_all = st.button("✂️", help="Prune All Volumes")

        with volumeCols[3]:
            refresh_all = st.button("🔄", help="Refresh All Volumes")

        edited_volumes_df = st.data_editor(df_volumes, 
                    hide_index=True,
                    disabled=("Name","Created"), 
                    column_config={
                        "Selected": st.column_config.CheckboxColumn(
                            "",
                            help="Select volumes for actions"
                        )
                    },
                    use_container_width=True)

        selected_volumes = edited_volumes_df[edited_volumes_df['Selected']]

        if inspect_all and not selected_volumes.empty:
            for _, row in selected_volumes.iterrows():
                volume_name = row['Name']
                volume = client.volumes.get(volume_name)
                st.write(volume.attrs)

        if remove_all and not selected_volumes.empty:
            for _, row in selected_volumes.iterrows():
                volume_name = row['Name']
                volume = client.volumes.get(volume_name)
                volume.remove(force=True)
            st.rerun()

        if prune_all:
            client.volumes.prune()  
            st.rerun()

        if refresh_all:
            st.rerun()
    else:
        st.info("No volumes found.")