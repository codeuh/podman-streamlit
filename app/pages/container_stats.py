import streamlit as st
from podman import PodmanClient
from components import (
    header,
    sidebar
)
import pandas as pd
import numpy as np
import altair as alt
import time
from datetime import datetime

def calculate_cpu_percent(current_stats, previous_stats):
    if not previous_stats:
        return 0.0
    
    cpu_delta = current_stats['CPUNano'] - previous_stats['CPUNano']
    system_delta = current_stats['SystemNano'] - previous_stats['SystemNano']
    
    if system_delta > 0:
        return (cpu_delta / system_delta) * 100.0
    return 0.0

def create_cpu_chart(data):
    # Ensure we have valid data
    if len(data) == 0 or data['cpu_percent'].isnull().all():
        # Create empty chart with domain
        return alt.Chart(pd.DataFrame({
            'timestamp': [datetime.now()],
            'cpu_percent': [0]
        })).mark_line(
            point=False
        ).encode(
            x=alt.X('timestamp:T', title='Time'),
            y=alt.Y('cpu_percent:Q', title='CPU (%)', scale=alt.Scale(domain=[0, 100])),
            tooltip=['timestamp:T', 'cpu_percent:Q']
        ).properties(height=250, title='CPU Usage')

    return alt.Chart(data).mark_line(
        point=False
    ).encode(
        x=alt.X('timestamp:T', title='Time'),
        y=alt.Y('cpu_percent:Q', title='CPU (%)', scale=alt.Scale(domain=[0, max(100, data['cpu_percent'].max() * 1.1)])),
        tooltip=['timestamp:T', 'cpu_percent:Q']
    ).properties(height=250, title='CPU Usage')

def create_memory_chart(data):
    # Ensure we have valid data
    if len(data) == 0 or data['memory_mb'].isnull().all():
        # Create empty chart with domain
        return alt.Chart(pd.DataFrame({
            'timestamp': [datetime.now()],
            'memory_mb': [0]
        })).mark_line(
            point=False,
            color='#00FF00'
        ).encode(
            x=alt.X('timestamp:T', title='Time'),
            y=alt.Y('memory_mb:Q', title='Memory (MB)', scale=alt.Scale(domain=[0, 1000])),
            tooltip=['timestamp:T', 'memory_mb:Q']
        ).properties(height=250, title='Memory Usage')

    max_memory = data['memory_mb'].max()
    return alt.Chart(data).mark_line(
        point=False,
        color='#00FF00'
    ).encode(
        x=alt.X('timestamp:T', title='Time'),
        y=alt.Y('memory_mb:Q', title='Memory (MB)', scale=alt.Scale(domain=[0, max_memory * 1.1])),
        tooltip=['timestamp:T', 'memory_mb:Q']
    ).properties(height=250, title='Memory Usage')

def create_network_chart(data):
    # Ensure we have valid data
    if len(data) == 0 or (data['rx_bytes'].isnull().all() and data['tx_bytes'].isnull().all()):
        # Create empty chart with domain
        empty_data = pd.DataFrame({
            'timestamp': [datetime.now()],
            'rx_bytes': [0],
            'tx_bytes': [0]
        })
        return alt.Chart(empty_data).transform_fold(
            ['rx_bytes', 'tx_bytes'],
            as_=['Metric', 'Value']
        ).mark_line(
            point=False
        ).encode(
            x=alt.X('timestamp:T', title='Time'),
            y=alt.Y('Value:Q', title='Network (KB/s)', scale=alt.Scale(domain=[0, 1000])),
            color=alt.Color('Metric:N'),
            tooltip=['timestamp:T', 'Value:Q', 'Metric:N']
        ).properties(height=250, title='Network Traffic')

    max_network = max(
        data['rx_bytes'].max() if not data['rx_bytes'].isnull().all() else 0,
        data['tx_bytes'].max() if not data['tx_bytes'].isnull().all() else 0
    )
    return alt.Chart(data).transform_fold(
        ['rx_bytes', 'tx_bytes'],
        as_=['Metric', 'Value']
    ).mark_line(
        point=False
    ).encode(
        x=alt.X('timestamp:T', title='Time'),
        y=alt.Y('Value:Q', title='Network (KB/s)', scale=alt.Scale(domain=[0, max_network * 1.1])),
        color=alt.Color('Metric:N'),
        tooltip=['timestamp:T', 'Value:Q', 'Metric:N']
    ).properties(height=250, title='Network Traffic')

def show_container_selector(client):
    containers = client.containers.list(all=True)
    container_options = [(None, "Select a container...")] + [(c.id, f"{c.name} ({c.short_id})") for c in containers]
    
    if 'current_container_id' not in st.session_state:
        st.session_state.current_container_id = None
    
    selected_id = st.selectbox(
        "Select Container",
        options=[id for id, _ in container_options],
        format_func=lambda x: next(name for id, name in container_options if id == x)
    )
    
    if selected_id != st.session_state.current_container_id:
        st.session_state.stats_data = []
        st.session_state.previous_stats = None
        st.session_state.current_container_id = selected_id
    
    return selected_id

def clear_placeholders():
    """Clear all placeholder widgets"""
    if 'placeholders' in st.session_state:
        for placeholder in st.session_state.placeholders.values():
            try:
                placeholder.empty()
            except:
                pass
        st.session_state.placeholders = {}

def cleanup_session_state():
    """Clean up session state when leaving the page"""
    # Clear placeholders first
    clear_placeholders()
    
    # Clean up other session state
    keys_to_clear = [
        'stats_data',
        'previous_stats',
        'current_container_id',
        'retention_seconds',
        'page_active'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def initialize_stats_data(seconds, end_time=None):
    """Initialize empty stats data for the specified number of seconds"""
    if end_time is None:
        end_time = datetime.now()
    return [
        {
            'timestamp': end_time - pd.Timedelta(seconds=i),
            'cpu_percent': 0.0,
            'memory_mb': 0.0,
            'rx_bytes': 0.0,
            'tx_bytes': 0.0
        }
        for i in range(seconds, 0, -1)
    ]

def get_network_interfaces(stats):
    return list(stats['Network'].keys())

def create_chart_containers():
    """Create the containers for the charts in vertical layout"""
    # Clear existing placeholders
    clear_placeholders()
    
    # Create placeholders for vertical layout
    st.session_state.placeholders['cpu'] = st.empty()
    st.session_state.placeholders['memory'] = st.empty()
    st.session_state.placeholders['network'] = st.empty()

def show_container_stats(client, container_id):
    # Initialize session state for page activity tracking
    if 'page_active' not in st.session_state:
        st.session_state.page_active = True
    
    # Reset page activity when the function starts
    st.session_state.page_active = True

    # Convert container_id to bytes before getting the container
    container_id_bytes = str(container_id).encode('utf-8')
    container = client.containers.get(container_id_bytes)
    container.reload()

    st.header(f"Container Stats: {container.name}")

    # Retention period control
    if 'retention_seconds' not in st.session_state:
        st.session_state.retention_seconds = 60
    
    st.session_state.retention_seconds = st.number_input(
        "Data retention period (seconds)", 
        min_value=10, 
        max_value=3600, 
        value=st.session_state.retention_seconds,
        help="How many seconds of historical data to keep in the charts"
    )

    if 'stats_data' not in st.session_state:
        st.session_state.stats_data = initialize_stats_data(st.session_state.retention_seconds)
    if 'previous_stats' not in st.session_state:
        st.session_state.previous_stats = None
    if 'placeholders' not in st.session_state:
        st.session_state.placeholders = {}

    # Create chart containers if they don't exist
    if not st.session_state.placeholders:
        create_chart_containers()

    try:
        stats_response = container.stats(stream=False, decode=True)
        current_stats = stats_response['Stats'][0]
        
        cpu_percent = calculate_cpu_percent(current_stats, st.session_state.previous_stats)
        
        network_interfaces = get_network_interfaces(current_stats)
        selected_interface = network_interfaces[0] if network_interfaces else None
        
        if not selected_interface:
            st.warning("No network interface available.")
            return

        if st.session_state.previous_stats:
            time_delta = (current_stats['SystemNano'] - st.session_state.previous_stats['SystemNano']) / 1e9
            rx_bytes = (current_stats['Network'][selected_interface]['RxBytes'] - 
                       st.session_state.previous_stats['Network'][selected_interface]['RxBytes']) / (1024 * time_delta)  # Convert to KB/s
            tx_bytes = (current_stats['Network'][selected_interface]['TxBytes'] - 
                       st.session_state.previous_stats['Network'][selected_interface]['TxBytes']) / (1024 * time_delta)  # Convert to KB/s
        else:
            rx_bytes = tx_bytes = 0
        
        current_time = datetime.now()
        record = {
            'timestamp': current_time,
            'cpu_percent': cpu_percent,
            'memory_mb': current_stats['MemUsage'] / (1024 * 1024),
            'rx_bytes': rx_bytes,
            'tx_bytes': tx_bytes
        }
        
        max_points = st.session_state.retention_seconds
        current_points = len(st.session_state.stats_data)
        
        if current_points > max_points:
            st.session_state.stats_data = st.session_state.stats_data[-max_points:]
        elif current_points < max_points:
            padding_needed = max_points - current_points
            if current_points > 0:
                oldest_time = st.session_state.stats_data[0]['timestamp']
                padding = initialize_stats_data(padding_needed, oldest_time)
                st.session_state.stats_data = padding + st.session_state.stats_data
            else:
                st.session_state.stats_data = initialize_stats_data(max_points - 1, current_time)
        
        st.session_state.stats_data.append(record)
        st.session_state.previous_stats = current_stats

        try:
            # Create DataFrame and ensure timestamp is datetime type
            stats_df = pd.DataFrame(st.session_state.stats_data)
            stats_df['timestamp'] = pd.to_datetime(stats_df['timestamp'])
            
            # Remove any rows with NaT timestamps or infinite values
            stats_df = stats_df.replace([np.inf, -np.inf], np.nan)
            stats_df = stats_df.dropna(subset=['timestamp'])

            # Update charts
            if 'placeholders' in st.session_state:
                st.session_state.placeholders['cpu'].altair_chart(create_cpu_chart(stats_df), use_container_width=True)
                st.session_state.placeholders['memory'].altair_chart(create_memory_chart(stats_df), use_container_width=True)
                st.session_state.placeholders['network'].altair_chart(create_network_chart(stats_df), use_container_width=True)
        except Exception as e:
            # If we can't update the charts, the page is probably being unmounted
            st.error(f"Error updating charts: {str(e)}")
            return

        # Check if we should continue updating
        if st.session_state.page_active:
            time.sleep(1)
            st.rerun()
    except Exception as e:
        st.error(f"Error updating stats: {str(e)}")
        if st.session_state.page_active:
            time.sleep(1)
            st.rerun()

def main():
    # Check if we're coming from a different page
    if 'current_page' in st.session_state and st.session_state.current_page != "container_stats":
        cleanup_session_state()
    
    # Set current page
    st.session_state.current_page = "container_stats"
    
    # Configure page
    st.set_page_config(page_title="Container Stats", layout="wide")
    
    # Initialize page state
    if 'page_active' not in st.session_state:
        st.session_state.page_active = True
    
    header.show()

    try:
        selected_uri = sidebar.show_uri_selector()
        with PodmanClient(base_url=selected_uri, identity="~/.ssh/id_ed25519") as client:
            sidebar.show_details(client)
            
            # Only proceed if the page is still active
            if st.session_state.page_active:
                container_id = show_container_selector(client)
            if container_id is not None:
                show_container_stats(client, container_id)
            else:
                st.info("Please select a container to view its statistics.")
    except Exception as e:
        st.exception(e)

if __name__ == "__main__":
    main()