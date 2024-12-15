import streamlit as st
import pandas as pd

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

        for pod in pods:
            created_timestamp = pod.attrs.get("Created", 0)

            pod_data.append({
                "Selected": False,
                "Name": pod.name,
                "ID": pod.short_id,
                "Created": created_timestamp,
            })

        df_pods = pd.DataFrame(pod_data)

        podCols = st.columns((1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))

        with podCols[0]:
            inspect_all = st.button("🔍", help="Inspect Pod")

        with podCols[1]:
            remove_all = st.button("🗑️", help="Remove Pod")

        with podCols[2]:
            start_all = st.button("▶️", help="Start Pod")

        with podCols[3]:
            stop_all = st.button("⏹️", help="Stop Pod")

        with podCols[4]:
            refresh_all = st.button("🔄", help="Refresh Pods")

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

        if remove_all and not selected_pods.empty:
            for _, row in selected_pods.iterrows():
                pod_name = row['Name']
                pod = client.pods.get(pod_name)
                pod.remove(force=True)
            st.rerun()

        if start_all and not selected_pods.empty:
            for _, row in selected_pods.iterrows():
                pod_name = row['Name']
                pod = client.pods.get(pod_name)
                pod.start()
            st.rerun()

        if stop_all and not selected_pods.empty:
            for _, row in selected_pods.iterrows():
                pod_name = row['Name']
                pod = client.pods.get(pod_name)
                pod.stop(timeout=10)
            st.rerun()

        if refresh_all:
            st.rerun()
    else:
        st.info("No pods found.")