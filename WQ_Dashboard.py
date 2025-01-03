#!/usr/bin/env python
# coding: utf-8

# Create a dashboard to illustrate trends in various water quality features with time

# In[1]:
#pip install streamlit-folium;

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import altair as alt

# 1. LOAD DATA
@st.cache_data
def load_data():
    # Replace with your actual data path
    df = pd.read_csv("SF_water.csv", parse_dates=["SampleDate"])
    return df

def main():
    st.title("Big Sioux River: Water Quality Dashboard")

    # -- Load the data --
    new_df = load_data()
    
    # --------------------------------------------------------------.c-------------------
    # 2. FOLIUM MAP (using your custom markers for specific sites)
    # ---------------------------------------------------------------------------------

    # Coordinates for a sampling location
    sampling_locations = [
        {"location": "Big Sioux River @ I-90",       "lat": 43.610284, "lon": -96.744755},
        {"location": "Big Sioux River @ Timberline", "lat": 43.599841, "lon": -96.653049},
        {"location": "Big Sioux River @ Bahnson",    "lat": 43.569702, "lon": -96.684698},
        {"location": "Skunk Creek @ Marion Road",    "lat": 43.533863, "lon": -96.790952},
        {"location": "Big Sioux River @ Falls Park", "lat": 43.556980, "lon": -96.722439}
    ]

    # "Smithfield Foods" coordinates
    smithfield_location = {"location": "Smithfield Foods",       "lat": 43.562259,         "lon": -96.719821}
    sfwwt_location       = {"location": "SF Waste Water Treatment","lat": 43.594920,        "lon": -96.661289}
    williams_location    = {"location": "Williams Disposal Pit (Superfund)", 
                            "lat": 43.545033086692605, 
                            "lon": -96.79196640241707}

    # Create a map centered on a general area
    map_center = [43.580, -96.720]  # Approximate center of all points
    water_quality_map = folium.Map(location=map_center, zoom_start=12)

    # Add markers for each sampling location
    for site in sampling_locations:
        folium.Marker(
            location=[site["lat"], site["lon"]],
            popup=site["location"],  # Display only the location name
            icon=folium.Icon(color="blue", icon="info-sign"),  # Blue marker
        ).add_to(water_quality_map)

    # Add a red marker for Smithfield Foods
    folium.Marker(
        location=[smithfield_location["lat"], smithfield_location["lon"]],
        popup=smithfield_location["location"],
        icon=folium.Icon(color="red", icon="info-sign"),  # Red marker
    ).add_to(water_quality_map)

    # Add a red marker for SF Waste Water Treatment
    folium.Marker(
        location=[sfwwt_location["lat"], sfwwt_location["lon"]],
        popup=sfwwt_location["location"],
        icon=folium.Icon(color="red", icon="info-sign"),  # Red marker
    ).add_to(water_quality_map)

    # Add a red marker for Williams Disposal Pit (Superfund)
    folium.Marker(
        location=[williams_location["lat"], williams_location["lon"]],
        popup=williams_location["location"],
        icon=folium.Icon(color="red", icon="info-sign"),  # Red marker
    ).add_to(water_quality_map)

    # Display the map in Streamlit
    st.write("## Water Quality Map")
    st_folium(water_quality_map, width=700, height=500)

    # ---------------------------------------------------------------------------------
    # 3. AUTO-SCALING SCATTER PLOT (SampleDate on x-axis; user picks y-axis)
    # ---------------------------------------------------------------------------------

    # Identify numeric columns (excluding columns you don't want to plot)
    numeric_cols = ['pH', 'Ammonia','EColi', 'Nitrate','DissolvedOxygen','TotalSuspendedSolids', 'Temperature']

    # Let user pick which feature to plot on the y-axis
    selected_feature = st.selectbox(
        "Select a feature for the y-axis:",
        numeric_cols
    )

    # Build Altair scatter plot
    scatter_chart = (
        alt.Chart(new_df)
        .mark_circle(size=30)
        .encode(
            x=alt.X("SampleDate:T", title="Sample Date"),
            y=alt.Y(selected_feature, title=selected_feature, scale=alt.Scale(zero=False)),
            tooltip=["SampleDate", selected_feature]
        )
        .properties(
            width="container",
            height=400,
            title=f"{selected_feature} over time"
        )
        .interactive()  # enables zooming/panning in the chart
    )

    st.write("## Time-Series Scatter Plot")
    st.altair_chart(scatter_chart, use_container_width=True)

    # ---------------------------------------------------------------------------------
    # 4. HISTOGRAM OF pH BY LOCATION (user selects Location)
    # ---------------------------------------------------------------------------------

#def main():
    st.title("Water Quality Dashboard with pH Stats Annotation")

    # Let user select location
    locations = new_df["Location"].unique()
    selected_location = st.selectbox("Select a location for the pH histogram", locations)

    # Filter for selected location
    filtered_df = new_df[new_df["Location"] == selected_location]

    if filtered_df.empty:
        st.warning(f"No data available for {selected_location}")
        return

    # -------------------------------------------------------------------
    # 2) Calculate mean and std dev of pH
    # -------------------------------------------------------------------
    mean_pH = filtered_df["pH"].mean()
    std_pH = filtered_df["pH"].std()

    # -------------------------------------------------------------------
    # 3) Base histogram
    # -------------------------------------------------------------------
    hist_chart = (
        alt.Chart(filtered_df)
        .mark_bar()
        .encode(
            x=alt.X("pH:Q", bin=alt.Bin(maxbins=30), title="pH"),
            y=alt.Y("count()", title="Count"),
            tooltip=["count()"]
        )
        .properties(
            width="container",
            height=300,
            title=f"Distribution of pH at {selected_location}"
        )
    )

    # -------------------------------------------------------------------
    # 4) Text annotation layer (upper-left corner)
    # -------------------------------------------------------------------
    annotation_text = (
        alt.Chart(pd.DataFrame([{}]))   # an empty data source
        .mark_text(align="left", baseline="top", color="red", fontSize=12)
        .encode(
            x=alt.value(20),  # 20 px from the left
            y=alt.value(20),  # 20 px from the top
            text=alt.value(f"Mean pH: {mean_pH:.2f} ± {std_pH:.2f}")
        )
    )

    final_hist_chart = alt.layer(hist_chart, annotation_text).configure_view(clip=False)

    # -------------------------------------------------------------------
    # 5) Display in Streamlit
    # -------------------------------------------------------------------
    st.altair_chart(final_hist_chart, use_container_width=True)

if __name__ == "__main__":
    main()



# In[ ]:




