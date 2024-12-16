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
    st.header("🖼️ Podman Images")
    images = client.images.list(all=True)

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
                "Selected": False,
                "Tags": image.tags,
                "ID": image.short_id,
                "Size (MB)": round(image.attrs.get("Size", 0) / 1024 / 1024, 2),
                "Created": readable_time,
            })

        df_images = pd.DataFrame(image_data)

        imageCols = st.columns((1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))

        with imageCols[0]:
            inspect_all = st.button("🔍", help="Inspect Image")

        with imageCols[1]:
            pull_all = st.button("📥", help="Pull Image")

        with imageCols[2]:
            remove_all = st.button("🗑️", help="Remove Image")

        with imageCols[3]:
            if st.button("✂️", help="Prune Images"):
                client.images.prune()  
                client.images.prune_builds()
                st.rerun()
        with imageCols[4]:
            refresh_all = st.button("🔄", help="Refresh Images")

        edited_images_df = st.data_editor(df_images, 
                            hide_index=True,
                            disabled=("Tags","ID","Size (MB)","Created"), 
                            column_config={
                                "Selected": st.column_config.CheckboxColumn(
                                    "",
                                    help="Select images for actions"
                                )
                            },
                            use_container_width=True)

        selected_images = edited_images_df[edited_images_df['Selected']]

        if inspect_all and not selected_images.empty:
            for _, row in selected_images.iterrows():
                image = client.images.get(row['ID'])
                st.write(image.attrs)

        if pull_all and not selected_images.empty:
            for _, row in selected_images.iterrows():
                client.images.pull(row['Tags'][0])
            st.rerun()

        if remove_all and not selected_images.empty:
            for _, row in selected_images.iterrows():
                client.images.remove(row['ID'], force=True)
            st.rerun()
        
        if refresh_all:
            st.rerun()

    else:
        st.info("No images found.")