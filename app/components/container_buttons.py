import streamlit as st
from utils import container_utils

# inspect button
def show_inspect(col):
    """
    Display the inspect button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("🔍", help="Inspect Selected Containers")
    
def handle_inspect(inspect, selected_containers):
    """
    Handle the inspect button action.

    Parameters:
        inspect (bool): The state of the inspect button.
        selected_containers (DataFrame): The DataFrame of selected containers.

    Returns:
        None
    """
    if inspect and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            st.write(container.attrs)

# links button
def show_links(col):
    """
    Display the show links button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("🌐", help="Show Selected Links")
    
def handle_links(show_links, selected_containers):
    """
    Handle the show links button action.

    Parameters:
        show_links (bool): The state of the show links button.
        selected_containers (DataFrame): The DataFrame of selected containers.

    Returns:
        None
    """
    if show_links and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            ports = container.attrs['NetworkSettings']['Ports']
            if ports:
                for port, mappings in ports.items():
                    if mappings:
                        host_port = mappings[0]['HostPort']
                        url = f"http://localhost:{host_port}"
                        st.write(f"{container.name}: {url}")

# logs button
def show_logs(col):
    """
    Display the show logs button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("📄", help="Show Selected Logs")

def handle_logs(logs, selected_containers):
    """
    Handle the show logs button action.

    Parameters:
        logs (bool): The state of the show logs button.
        selected_containers (DataFrame): The DataFrame of selected containers.

    Returns:
        None
    """
    if logs and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            logs = container.logs(stream=False, stdout=True, stderr=True)

            st.subheader(f"{row['Name']}'s Logs")

            log_placeholder = st.empty()
            log_lines = []

            for log_line in logs:
                decoded_log_line = log_line.decode('utf-8').strip()
                if decoded_log_line:
                    log_lines.append(decoded_log_line)
            log_placeholder.code("\n".join(log_lines), "log")

# generate quadlet button
def show_generate_quadlet(col):
    """
    Display the generate quadlet button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("📜", help="Generate Selected Quadlets")
    
def handle_generate_quadlet(generate_quadlet, selected_containers, client):
    """
    Handle the generate quadlet button action.

    Parameters:
        generate_quadlet (bool): The state of the generate quadlet button.
        selected_containers (DataFrame): The DataFrame of selected containers.
        client (PodmanClient): The client object used to interact with the containers.

    Returns:
        None
    """
    if generate_quadlet and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container_utils.run_podlet(client, row["Name"], row['RunCommand'])

# exec button
def show_exec(col):
    """
    Display the exec button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("⚙️", help="Execute in Container")

def handle_exec(container_exec, df_containers, selected_containers):
    """
    Handle the exec button action.

    Parameters:
        container_exec (bool): The state of the exec button.
        df_containers (DataFrame): The DataFrame of all containers.
        selected_containers (DataFrame): The DataFrame of selected containers.

    Returns:
        None
    """
    if container_exec:
        container_utils.execute(df_containers, selected_containers['Name'].tolist())

    if "execute_outputs" in st.session_state:
        with st.expander("Execution Outputs", True):
            if st.button("Clear Outputs"):
                del st.session_state["execute_outputs"]
                st.rerun()
            if st.session_state.execute_outputs:
                st.subheader("Command executed:")
                st.code(st.session_state.execute_outputs[0]['command'], "bash")
            for output in st.session_state.execute_outputs:
                st.subheader(f"{output['container']}'s output:")
                st.code(output['output'], "text")

# start button
def show_start(col):
    """
    Display the start button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("▶️", help="Start Selected Containers")
    
def handle_start(start, selected_containers):
    """
    Handle the start button action.

    Parameters:
        start (bool): The state of the start button.
        selected_containers (DataFrame): The DataFrame of selected containers.

    Returns:
        None
    """
    if start and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            if container.status == "paused":
                container.unpause()
            elif container.status == "exited":
                container.start(force=True)
        st.rerun()

# pause button
def show_pause(col):
    """
    Display the pause button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("⏸️", help="Pause Selected Containers")

def handle_pause(pause, selected_containers):
    """
    Handle the pause button action.

    Parameters:
        pause (bool): The state of the pause button.
        selected_containers (DataFrame): The DataFrame of selected containers.

    Returns:
        None
    """
    if pause and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            if container.status == "running":
                container.pause()
        st.rerun()

# stop button
def show_stop(col):
    """
    Display the stop button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("⏹️", help="Stop Selected Containers")

def handle_stop(stop, selected_containers):
    """
    Handle the stop button action.

    Parameters:
        stop (bool): The state of the stop button.
        selected_containers (DataFrame): The DataFrame of selected containers.

    Returns:
        None
    """
    if stop and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            if container.status != "paused":
                container.stop()
            else:
                container.kill()
        st.rerun()

# remove button
def show_remove(col):
    """
    Display the remove button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("🗑️", help="Remove Selected Containers")
    
def handle_remove(remove, selected_containers):
    """
    Handle the remove button action.

    Parameters:
        remove (bool): The state of the remove button.
        selected_containers (DataFrame): The DataFrame of selected containers.

    Returns:
        None
    """
    if remove and not selected_containers.empty:
        for _, row in selected_containers.iterrows():
            container = st.session_state.container_objects[row['ID']]
            container.remove(force=True)
        st.rerun()

# prune button
def show_prune(col):
    """
    Display the prune button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("✂️", help="Prune All Containers")

def handle_prune(prune, client):
    """
    Handle the prune button action.

    Parameters:
        prune (bool): The state of the prune button.
        client (PodmanClient): The client object used to interact with the containers.

    Returns:
        None
    """
    if prune:
        client.containers.prune()
        st.rerun()

# refresh button
def show_refresh(col):
    """
    Display the refresh button.

    Parameters:
        col (streamlit.delta_generator.DeltaGenerator): The Streamlit column to place the button in.

    Returns:
        bool: True if the button is clicked, False otherwise.
    """
    with col:
        return st.button("🔄", help="Refresh All Containers")

def handle_refresh(refresh, client):
    """
    Handle the refresh button action.

    Parameters:
        refresh (bool): The state of the refresh button.
        client (PodmanClient): The client object used to interact with the containers.

    Returns:
        None
    """
    if refresh:
        st.rerun()