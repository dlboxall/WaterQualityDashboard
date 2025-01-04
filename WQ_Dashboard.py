#!/usr/bin/env python
# coding: utf-8

# Create a dashboard to illustrate trends in various water quality features with time

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

# MAIN FUNCTION
def main():
    # Title of the dashboard
    st.title("Big Sioux River: Water Quality Dashboard")

    # Load the data
    new_df = load_data()

    # ---------------------------------------------------------------------------------
    # 2. FOLIUM MAP (with custom markers for specific sites)
    # ---------------------------------------------------------------------------------
    # Sampling locations
    sampling_locations = [
        {"location": "Big Sioux River @ I-90", "lat": 43.610284, "lon": -96.744755},
        {"location": "Big Sioux River @ Timberline", "lat": 43.599841, "lon": -96.653049},
        {"location": "Big Sioux River @ Bahnson", "lat": 43.569702, "lon": -96.684698},
        {"location": "Skunk Creek @ Marion Road", "lat": 43.533863, "lon": -96.790952},
        {"location": "Big Sioux River @ Falls Park", "lat": 43.556980, "lon": -96.722439}
    ]

    # Other important locations
    smithfield_location = {"location": "Smithfield Foods", "lat": 43.562259, "lon": -96.719821}
    sfwwt_location = {"location": "SF Waste Water Treatment", "lat": 43.594920, "lon": -96.661289}
    williams_location = {
        "location": "Williams Disposal Pit (Superfund)", 
        "lat": 43.545033086692605, 
        "lon": -96.79196640241707
    }

    # Create a map centered on a general area
    map_center = [43.580, -96.720]
    water_quality_map = folium.Map(location=map_center, zoom_start=12)

    # Add markers for sampling locations
    for site in sampling_locations:
        folium.Marker(
            location=[site["lat"], site["lon"]],
            popup=site["location"],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(water_quality_map)

    # Add markers for other locations
    for loc in [smithfield_location, sfwwt_location, williams_location]:
        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            popup=loc["location"],
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(water_quality_map)

    # Display the map in Streamlit
    st.write("## Water Quality Map")
    st_folium(water_quality_map, width=700, height=500)

    # ---------------------------------------------------------------------------------
    # 3. AUTO-SCALING SCATTER PLOT
    # ---------------------------------------------------------------------------------
    feature_units = {
        "Nitrate": "Nitrate (ppm)",
        "DissolvedOxygen": "Dissolved Oxygen (ppm)",
        "Ammonia": "Ammonia (ppm)",
        "EColi": "E. coli (CFU)",
        "TotalSuspendedSolids": "Total Suspended Solids (ppm)",
        "Temperature": "Temperature (°C)"
    }

    numeric_cols = ['pH', 'Ammonia', 'EColi', 'Nitrate', 'DissolvedOxygen', 'TotalSuspendedSolids', 'Temperature']

    selected_feature = st.selectbox("Select a feature for the y-axis:", numeric_cols)
    y_axis_title = feature_units.get(selected_feature, selected_feature)

    scatter_chart = (
        alt.Chart(new_df)
        .mark_circle(size=30)
        .encode(
            x=alt.X("SampleDate:T", title="Sample Date"),
            y=alt.Y(selected_feature, title=y_axis_title, scale=alt.Scale(zero=False)),
            tooltip=["SampleDate", selected_feature]
        )
        .properties(
            width="container",
            height=400,
            title=f"{y_axis_title} over time"
        )
        .interactive()
    )

    st.write("## Time-Series Scatter Plot")
    st.altair_chart(scatter_chart, use_container_width=True)
'''
    # ---------------------------------------------------------------------------------
    # 4. HISTOGRAM OF pH BY LOCATION
    # ---------------------------------------------------------------------------------
    st.write("## pH Histograms by Location")

    locations = new_df["Location"].unique()
    selected_location = st.selectbox("Select a location for the pH histogram", locations)

    filtered_df = new_df[new_df["Location"] == selected_location]
    mean_pH = filtered_df["pH"].mean()
    std_pH = filtered_df["pH"].std()

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

    annotation_text = (
        alt.Chart(pd.DataFrame([{}]))
        .mark_text(align="left", baseline="top", color="red", fontSize=12)
        .encode(
            x=alt.value(20),
            y=alt.value(20),
            text=alt.value(f"Mean pH: {mean_pH:.2f} ± {std_pH:.2f}")
        )
    )

    final_hist_chart = alt.layer(hist_chart, annotation_text).configure_view(clip=False)
    st.altair_chart(final_hist_chart, use_container_width=True)
'''    
# ---------------------------------------------------------------------------------
# 4. HISTOGRAM OF pH BY LOCATION
# ---------------------------------------------------------------------------------
st.write("## pH Histograms by Location")

# 1) Add "All locations" as the first item in the selection box
unique_locations = new_df["Location"].unique().tolist()
location_options = ["All locations"] + unique_locations
selected_location = st.selectbox("Select a location for the pH histogram", location_options)

# 2) Define a color scale for your five known locations
color_scale = alt.Scale(
    domain=[
        "Big Sioux River @ Bahnson",
        "Big Sioux River @ Falls Park",
        "Big Sioux River @ I-90",
        "Big Sioux River @ Timberline",
        "Skunk Creek @ Marion Road"
    ],
    range=["blue", "orange", "green", "red", "purple"]
)

# We'll use a constant opacity so that overlaid histograms and single histograms match
opacity_value = 0.5

if selected_location == "All locations":
    # 3) Overlay histograms for all five locations
    #    We layer one histogram per location
    layered_charts = []

    for loc in color_scale.domain:
        loc_df = new_df[new_df["Location"] == loc]

        # Build the histogram layer for this location
        loc_hist = (
            alt.Chart(loc_df)
            .mark_bar(opacity=opacity_value)
            .encode(
                x=alt.X(
                    "pH:Q",
                    bin=alt.Bin(maxbins=30),
                    # Initial domain 3–12, but can pan/zoom to 0–14
                    scale=alt.Scale(domain=[3, 12]),  
                    title="pH",
                ),
                y=alt.Y(
                    "count()",
                    # Initial domain 0–600, but can pan/zoom further
                    scale=alt.Scale(domain=[0, 600]),
                    title="Count",
                ),
                # Use a fixed color for each location
                color=alt.value(color_scale.range[color_scale.domain.index(loc)]),
                tooltip=["count()"]
            )
        )

        layered_charts.append(loc_hist)

    # Combine (layer) all location charts
    hist_chart = alt.layer(*layered_charts).properties(
        width="container",
        height=300,
        title="Distribution of pH for All Locations"
    )

    # If you want the user to be able to pan/zoom, add .interactive()
    final_hist_chart = hist_chart.interactive()

else:
    # 4) Show a single histogram for the selected location
    filtered_df = new_df[new_df["Location"] == selected_location]
    mean_pH = filtered_df["pH"].mean()
    std_pH = filtered_df["pH"].std()

    # Build the histogram for just one location
    hist_chart = (
        alt.Chart(filtered_df)
        .mark_bar(opacity=opacity_value)
        .encode(
            x=alt.X(
                "pH:Q",
                bin=alt.Bin(maxbins=30),
                scale=alt.Scale(domain=[3, 12]),
                title="pH"
            ),
            y=alt.Y(
                "count()",
                scale=alt.Scale(domain=[0, 600]),
                title="Count"
            ),
            color=alt.Color("Location:N", scale=color_scale, legend=None),
            tooltip=["count()"]
        )
        .properties(
            width="container",
            height=300,
            title=f"Distribution of pH at {selected_location}"
        )
    )

    # Add a mean ± std annotation
    annotation_text = (
        alt.Chart(pd.DataFrame([{}]))
        .mark_text(align="left", baseline="top", color="red", fontSize=12)
        .encode(
            x=alt.value(20),
            y=alt.value(20),
            text=alt.value(f"Mean pH: {mean_pH:.2f} ± {std_pH:.2f}")
        )
    )

    # Layer the histogram and the annotation
    final_hist_chart = alt.layer(hist_chart, annotation_text).interactive()

# 5) Render the final chart in the Streamlit app
st.altair_chart(final_hist_chart, use_container_width=True)

if __name__ == "__main__":
    main()
