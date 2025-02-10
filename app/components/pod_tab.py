import streamlit as st
import pandas as pd
from utils.status_icons import *
from dateutil import parser 
from tzlocal import get_localzone

def show_pod_tab(client):
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

        podCols = st.columns((1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))

        with podCols[0]:
            inspect_all = st.button("🔍", help="Inspect Selected Pods")

        with podCols[1]:
            start_all = st.button("▶️", help="Start Selected Pods")

        with podCols[2]:
            pause_all = st.button("⏸️", help="Pause Selected Pods")

        with podCols[3]:
            stop_all = st.button("⏹️", help="Stop Selected Pods")

        with podCols[4]:
            remove_all = st.button("🗑️", help="Remove Selected Pods")
        
        with podCols[5]:
            if st.button("✂️", help="Prune All Pods"):
                client.pods.prune()  
                st.rerun()

        with podCols[6]:
            refresh_all = st.button("🔄", help="Refresh All Pods")

        edited_pods_df = st.data_editor(df_pods, 
                    hide_index=True,
                    disabled=("Name","Created","Status"), 
                    column_config={
                        "Selected": st.column_config.CheckboxColumn(
                            "",
                            help="Select pods for actions"
                        )
                    },
                    use_container_width=True)

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