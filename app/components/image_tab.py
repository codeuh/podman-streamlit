import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

def show_image_tab(client):
    """
    Displays a tab in Streamlit that shows information about Podman images.

    This function connects to the client, retrieves a list of available images,
    and displays their details, including tags, IDs, sizes, and creation times.
    
    Args:
        client (PodmanClient): A client object used to connect to the container runtime.
        
    Returns:
        None
    """
    st.header("📦 Podman Images")
    images = client.images.list()

    if images:
        image_data = []
        local_timezone = datetime.now().astimezone().tzinfo
        now = datetime.now(local_timezone)
        for image in images:
            created_timestamp = image.attrs.get("Created", 0)
            created_time = datetime.fromtimestamp(created_timestamp, local_timezone)
            relative_time = relativedelta(now, created_time)

            if relative_time.years:
                readable_time = f"{relative_time.years} years, {relative_time.months} months, {relative_time.days} days ago"
            elif relative_time.months:
                readable_time = f"{relative_time.months} months, {relative_time.days} days ago"
            elif relative_time.days:
                readable_time = f"{relative_time.days} days ago"
            elif relative_time.hours:
                readable_time = f"{relative_time.hours} hours, {relative_time.minutes} minutes ago"
            else:
                readable_time = f"{relative_time.minutes} minutes ago"

            image_data.append({
                "Tags": image.tags,
                "ID": image.short_id,
                "Size (MB)": round(image.attrs.get("Size", 0) / 1024 / 1024, 2),
                "Created": readable_time,
            })

        df_images = pd.DataFrame(image_data)

        st.dataframe(df_images, hide_index=True, use_container_width=True)
    else:
        st.info("No images found.")