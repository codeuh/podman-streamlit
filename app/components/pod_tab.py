import streamlit as st
import pandas as pd
from utils.status_icons import *
from dateutil import parser 
from tzlocal import get_localzone

def show(client):
    """
    Displays a tab in Streamlit that shows information about Podman pods.

    This function connects to the client, retrieves a list of available pods,
    and displays their details, including names and creation times.
    
    Args:
        client (PodmanClient): A client object used to connect to the container runtime.
        
    Returns:
        None
    """
    st.header("🫛 Podman Pods")
    pods = client.pods.list()
    if pods:
        pod_data = []
        my_timezone = get_localzone()
        for pod in pods:
            created_timestamp = pod.attrs["Created"]
            created_time = parser.isoparse(created_timestamp).astimezone(my_timezone)
            containers = pod.attrs['Containers']
            status_icon = "".join(
                status_icons.get(c['Status'], '❓') for c in containers
            )

            pod_data.append({
                "Selected": False,
                "Name": pod.name,
                "Status": status_icon,
                "ID": pod.short_id,
                "Created": created_time,
            })

        df_pods = pd.DataFrame(pod_data)

        action = st.selectbox(
            "Pod Actions",
            [
                "Select action...",
                "🔍 Inspect",
                "▶️ Start",
                "⏸️ Pause",
                "⏹️ Stop",
                "🗑️ Remove",
                "✂️ Prune",
                "🔄 Refresh"
            ]
        )

        # Convert dropdown selection to button clicks
        inspect_all = action == "🔍 Inspect"
        start_all = action == "▶️ Start"
        pause_all = action == "⏸️ Pause"
        stop_all = action == "⏹️ Stop"
        remove_all = action == "🗑️ Remove"
        prune_all = action == "✂️ Prune"
        refresh_all = action == "🔄 Refresh"

        if prune_all:
            client.pods.prune()
            st.rerun()

        edited_pods_df = st.data_editor(df_pods, 
                    hide_index=True,
                    disabled=("Name","Created","Status"), 
                    column_config={
                        "Selected": st.column_config.CheckboxColumn(
                            "",
                            help="Select pods for actions"
                        )
                    },
                    width="stretch")

        selected_pods = edited_pods_df[edited_pods_df['Selected']]

        if inspect_all and not selected_pods.empty:
            for _, row in selected_pods.iterrows():
                pod_name = row['Name']
                pod = client.pods.get(pod_name)
                st.write(pod.attrs)

        if start_all and not selected_pods.empty:
            for _, row in selected_pods.iterrows():
                pod_name = row['Name']
                pod = client.pods.get(pod_name)
                if pod.attrs['State'] == 'Paused':
                    pod.unpause()
                elif  pod.attrs['State'] == 'Exited':
                    pod.start()
            st.rerun()

        if pause_all and not selected_pods.empty:
            for _, row in selected_pods.iterrows():
                pod_name = row['Name']
                pod = client.pods.get(pod_name)
                if pod.attrs['State'] == 'Running':
                    pod.pause()
            st.rerun()

        if stop_all and not selected_pods.empty:
            for _, row in selected_pods.iterrows():
                pod_name = row['Name']
                pod = client.pods.get(pod_name)
                if pod.attrs['State'] != 'Paused':
                    pod.stop(timeout=10)
            st.rerun()

        if remove_all and not selected_pods.empty:
            for _, row in selected_pods.iterrows():
                pod_name = row['Name']
                pod = client.pods.get(pod_name)
                pod.remove(force=True)
            st.rerun()

        if refresh_all:
            st.rerun()
    else:
        st.info("No pods found.")