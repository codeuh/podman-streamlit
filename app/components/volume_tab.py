import streamlit as st
import pandas as pd
from dateutil import parser 
from tzlocal import get_localzone

def show(client):
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
        my_timezone = get_localzone()
        for volume in volumes:
            created_timestamp = volume.attrs["CreatedAt"]
            created_time = parser.isoparse(created_timestamp).astimezone(my_timezone)
            volume_data.append({
                "Selected": False,
                "Name": volume.name,
                "Scope": volume.attrs["Scope"],
                "Mount Point": f'{volume.attrs["Mountpoint"]}',
                "Created": created_time,
            })

        df_volumes = pd.DataFrame(volume_data)

        action = st.selectbox(
            "Volume Actions",
            [
                "Select action...",
                "🔍 Inspect",
                "🗑️ Remove",
                "✂️ Prune",
                "🔄 Refresh"
            ]
        )

        # Convert dropdown selection to button clicks
        inspect_all = action == "🔍 Inspect"
        remove_all = action == "🗑️ Remove"
        prune_all = action == "✂️ Prune"
        refresh_all = action == "🔄 Refresh"

        edited_volumes_df = st.data_editor(df_volumes, 
                    hide_index=True,
                    disabled=("Name","Created"), 
                    column_config={
                        "Selected": st.column_config.CheckboxColumn(
                            "",
                            help="Select volumes for actions"
                        )
                    },
                    width="stretch")

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