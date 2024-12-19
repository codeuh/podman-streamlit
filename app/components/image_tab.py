import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

import json

import json

@st.dialog("Pull Image")
def pull(client):
    """
    Opens a dialog to input the repository and tag for pulling an image.

    Args:
        client (PodmanClient): The client object used to interact with the container runtime.

    Returns:
        None
    """
    repository = st.text_input("Repository:")
    all_tags = st.checkbox("Pull all tags")
    
    if st.button("Pull"):
        try:
            with st.spinner("Pulling..."):
                output_placeholder = st.empty() 

                if all_tags:
                    output = client.images.pull(repository, all_tags=True)
                else:
                    output = client.images.pull(repository)

                output_placeholder.write("✅ **Image pulled successfully!**")

            st.session_state.pull = {"output": output}
            st.rerun()

        except Exception as e:
            st.error(str(e))

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
            inspect_all = st.button("🔍", help="Inspect Selected Images")

        with imageCols[1]:
            pull_all = st.button("📥", help="Pull Selected Images")

        with imageCols[2]:
            remove_all = st.button("🗑️", help="Remove Selected Images")

        with imageCols[3]:
            if st.button("✂️", help="Prune All Images"):
                client.images.prune()  
                client.images.prune_builds()
                st.rerun()
        with imageCols[4]:
            refresh_all = st.button("🔄", help="Refresh All Images")

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

        with st.expander("Advanced Image Tools"):
            imageToolsTab, otherTab = st.tabs(["Pull New Image", "Other"])
            
            with imageToolsTab:
                pullCols = st.columns(2)
                with pullCols[0]:
                    pull_image_button = st.button("📥 Pull New Image")
                with pullCols[1]:
                    pull_image_clear = st.button("Clear Output")
                if pull_image_button:
                    pull(client)
                if pull_image_clear:
                    if "pull" in st.session_state:
                        del st.session_state["pull"]

                if "pull" in st.session_state:
                    st.code(st.session_state.pull["output"])

    else:
        st.info("No images found.")