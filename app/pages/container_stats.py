import streamlit as st
from podman import PodmanClient
from components import (
    header,
    sidebar
)
import pandas as pd
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
    return alt.Chart(data).mark_line(
        point=False
    ).encode(
        x=alt.X('timestamp:T', title='Time'),
        y=alt.Y('cpu_percent:Q', title='CPU (%)'),
        tooltip=['timestamp:T', 'cpu_percent:Q']
    ).properties(height=250, title='CPU Usage')

def create_memory_chart(data):
    return alt.Chart(data).mark_line(
        point=False,
        color='#00FF00'
    ).encode(
        x=alt.X('timestamp:T', title='Time'),
        y=alt.Y('memory_mb:Q', title='Memory (MB)'),
        tooltip=['timestamp:T', 'memory_mb:Q']
    ).properties(height=250, title='Memory Usage')

def create_network_chart(data):
    return alt.Chart(data).transform_fold(
        ['rx_bytes', 'tx_bytes'],
        as_=['Metric', 'Value']
    ).mark_line(
        point=False
    ).encode(
        x=alt.X('timestamp:T', title='Time'),
        y=alt.Y('Value:Q', title='Network (KB/s)'),
        color=alt.Color('Metric:N'),
        tooltip=['timestamp:T', 'Value:Q', 'Metric:N']
    ).properties(height=250, title='Network Traffic')

def show_container_selector(client):
    containers = client.containers.list(all=True)
    container_options = [(c.id, f"{c.name} ({c.short_id})") for c in containers]
    
    if 'current_container_id' not in st.session_state:
        st.session_state.current_container_id = container_options[0][0]
    
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
    if 'placeholders' in st.session_state:
        for placeholder in st.session_state.placeholders.values():
            placeholder.empty()
    st.session_state.placeholders = {}

def initialize_stats_data(seconds, end_time=None):
    """Initialize empty stats data for the specified number of seconds"""
    if end_time is None:
        end_time = datetime.now()
    return [
        {
            'timestamp': end_time - pd.Timedelta(seconds=i),
            'cpu_percent': None,
            'memory_mb': None,
            'rx_bytes': None,
            'tx_bytes': None
        }
        for i in range(seconds, 0, -1)
    ]

def show_container_stats(client, container_id):
    container = client.containers.get(container_id)
    container.reload()

    st.header(f"Container Stats: {container.name}")

    col1, col2 = st.columns([1, 1])  
    with col1:
        if 'chart_layout' not in st.session_state:
            st.session_state.chart_layout = "horizontal"
        
        new_layout = st.radio(
            "Chart Layout",
            options=["horizontal", "vertical"],
            horizontal=True,
        )
        
        if new_layout != st.session_state.chart_layout:
            clear_placeholders()
            st.session_state.chart_layout = new_layout
    
    with col2:
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

    if not st.session_state.placeholders:
        if st.session_state.chart_layout == "horizontal":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.session_state.placeholders['cpu'] = st.empty()
            with col2:
                st.session_state.placeholders['memory'] = st.empty()
            with col3:
                st.session_state.placeholders['network'] = st.empty()
        else:
            st.session_state.placeholders['cpu'] = st.empty()
            st.session_state.placeholders['memory'] = st.empty()
            st.session_state.placeholders['network'] = st.empty()

    while True:
        
        stats_response = container.stats(stream=False, decode=True)
        current_stats = stats_response['Stats'][0]
        
        cpu_percent = calculate_cpu_percent(current_stats, st.session_state.previous_stats)
        
        if st.session_state.previous_stats:
            time_delta = (current_stats['SystemNano'] - st.session_state.previous_stats['SystemNano']) / 1e9
            rx_bytes = (current_stats['Network']['eth0']['RxBytes'] - 
                       st.session_state.previous_stats['Network']['eth0']['RxBytes']) / (1024 * time_delta)  # Convert to KB/s
            tx_bytes = (current_stats['Network']['eth0']['TxBytes'] - 
                       st.session_state.previous_stats['Network']['eth0']['TxBytes']) / (1024 * time_delta)  # Convert to KB/s
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
        
        max_points = st.session_state.retention_seconds
        if len(st.session_state.stats_data) > max_points:
            st.session_state.stats_data = st.session_state.stats_data[-max_points:]
        elif len(st.session_state.stats_data) < max_points:
            padding = initialize_stats_data(max_points - len(st.session_state.stats_data))
            st.session_state.stats_data = padding + st.session_state.stats_data

        stats_df = pd.DataFrame(st.session_state.stats_data)

        st.session_state.placeholders['cpu'].altair_chart(create_cpu_chart(stats_df), use_container_width=True)
        st.session_state.placeholders['memory'].altair_chart(create_memory_chart(stats_df), use_container_width=True)
        st.session_state.placeholders['network'].altair_chart(create_network_chart(stats_df), use_container_width=True)
        
        time.sleep(1)

def main():
    st.set_page_config(page_title="Container Stats", layout="wide")

    header.show()

    try:
        selected_uri = sidebar.show_uri_selector()
        with PodmanClient(base_url=selected_uri, identity="~/.ssh/id_ed25519") as client:
            sidebar.show_details(client)
            container_id = show_container_selector(client)
            show_container_stats(client, container_id)
    except Exception as e:
        st.exception(e)

if __name__ == "__main__":
    main()