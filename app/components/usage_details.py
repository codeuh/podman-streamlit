import streamlit as st
import pandas as pd
import altair as alt

def show_usage_details(client):
    resource_data = client.df()

    st.subheader("Containers")
    container_data = pd.DataFrame(resource_data["Containers"])
    container_data["Size_MB"] = container_data["Size"] / (1024 * 1024)

    container_chart = alt.Chart(container_data).mark_bar().encode(
        y=alt.Y("Names:N", sort="-x", title="Container Names"),
        x=alt.X("Size_MB:Q", title="Size (MB)"),
        color=alt.Color("Status:N", title="Status"),
        tooltip=["Names", "Status", "Size_MB"]
    ).properties(height=300)
    st.altair_chart(container_chart, use_container_width=True)

    st.subheader("Images")
    image_data = pd.DataFrame(resource_data["Images"])
    image_data["Size_MB"] = image_data["Size"] / (1024 * 1024)

    image_chart = alt.Chart(image_data).mark_bar().encode(
        y=alt.Y("Repository:N", sort="-x", title="Repository"),
        x=alt.X("Size_MB:Q", title="Size (MB)"),
        color=alt.Color("Tag:N", title="Tag"),
        tooltip=["Repository", "Tag", "Size_MB"]
    ).properties(height=300)
    st.altair_chart(image_chart, use_container_width=True)

    st.subheader("Volumes")
    volume_data = pd.DataFrame(resource_data["Volumes"])
    volume_data["Size_MB"] = volume_data["Size"] / (1024 * 1024)
    volume_data["ReclaimableSize_MB"] = volume_data["ReclaimableSize"] / (1024 * 1024)

    volume_chart = alt.Chart(volume_data).mark_bar().encode(
        y=alt.Y("VolumeName:N", sort="-x", title="Volume Name"),
        x=alt.X("Size_MB:Q", title="Size (MB)"),
        color=alt.Color("Links:Q", title="Links"),
        tooltip=["VolumeName", "Size_MB", "ReclaimableSize_MB", "Links"]
    ).properties(height=300)
    st.altair_chart(volume_chart, use_container_width=True)

    reclaimable_space = volume_data[volume_data["ReclaimableSize_MB"] > 0]
    st.write("Volumes with reclaimable space:")
    reclaimable_chart = alt.Chart(reclaimable_space).mark_bar().encode(
        y=alt.Y("VolumeName:N", sort="-x", title="Volume Name"),
        x=alt.X("ReclaimableSize_MB:Q", title="Reclaimable Size (MB)"),
        color=alt.Color("Links:Q", title="Links"),
        tooltip=["VolumeName", "ReclaimableSize_MB", "Links"]
    ).properties(height=300)
    st.altair_chart(reclaimable_chart, use_container_width=True)