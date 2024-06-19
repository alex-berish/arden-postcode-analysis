import streamlit as st
import pandas as pd
import plotly.express as px

# Set Streamlit to wide mode
st.set_page_config(layout="wide")

# Load the data
data = pd.read_csv('data.csv')

# Convert relevant columns to numeric types
data['Cost'] = pd.to_numeric(data['Cost'].str.replace('£', '').str.replace(',', ''), errors='coerce')
data['Conv. value'] = pd.to_numeric(data['Conv. value'].str.replace('£', '').str.replace(',', ''), errors='coerce')
data['Total CPE'] = pd.to_numeric(data['Total CPE'].str.replace('£', '').str.replace(',', ''), errors='coerce')
data['BL Traffic'] = pd.to_numeric(data['BL Traffic'], errors='coerce')
data['Direct BL CPE'] = pd.to_numeric(data['Direct BL CPE'].str.replace('£', '').str.replace(',', ''), errors='coerce')
data['Total Apps'] = pd.to_numeric(data['Total Apps'], errors='coerce')
data['Total App CPA'] = pd.to_numeric(data['Total App CPA'].str.replace('£', '').str.replace(',', ''), errors='coerce')
data['Total Direct Enrols'] = pd.to_numeric(data['Total Direct Enrols'], errors='coerce')

# Create a new column for tooltip header with fallback logic
data['tooltip_header'] = data.apply(lambda row: row['town'] if row['town'] != '0' else (row['region'] if row['region'] != '0' else row['Postcode (Matched)']), axis=1)

# Mapping of selectable pairs to their respective columns in the dataframe
pairings = {
    "BL Direct Enrols and Direct BL CPE": ["BL Direct Enrols", "Direct BL CPE"],
    "Total Apps and Total App CPA": ["Total Apps", "Total App CPA"],
    "Total Direct Enrols and Total CPE": ["Total Direct Enrols", "Total CPE"]
}

# Sidebar selection for pairing
selected_pairing = st.sidebar.selectbox(
    "Select Data Pairing",
    list(pairings.keys())
)

# Get columns for the selected pairing
columns_for_pairing = pairings[selected_pairing]

# Add sliders to filter the selected columns without decimal places
col1_min, col1_max = int(data[columns_for_pairing[0]].min()), int(data[columns_for_pairing[0]].max())
col2_min, col2_max = int(data[columns_for_pairing[1]].min()), int(data[columns_for_pairing[1]].max())

col1_range = st.sidebar.slider(f"Filter {columns_for_pairing[0]}", col1_min, col1_max, (col1_min, col1_max), key="slider1")
col2_range = st.sidebar.slider(f"Filter {columns_for_pairing[1]}", col2_min, col2_max, (col2_min, col2_max), key="slider2")

# Filter data based on slider values
filtered_data = data[(data[columns_for_pairing[0]].between(*col1_range)) & (data[columns_for_pairing[1]].between(*col2_range))]

# Check if filtered_data is empty
if filtered_data.empty:
    filtered_data = pd.DataFrame(columns=['latitude', 'longitude'] + list(columns_for_pairing))
    
    # Set a default center point for an empty map
    center_lat, center_lon = 54.0, -2.0
else:
    center_lat, center_lon = filtered_data['latitude'].mean(), filtered_data['longitude'].mean()

# Create the base map
fig = px.scatter_mapbox(
    filtered_data,
    lat='latitude',
    lon='longitude',
    hover_name='tooltip_header',
    mapbox_style='carto-positron',
    zoom=5
)

# Add columns for pairing to customdata
fig.update_traces(
    hovertemplate=(
        '<b>%{hovertext}</b><br>' +
        f'{columns_for_pairing[0]}: %{{customdata[0]}}<br>' +
        f'{columns_for_pairing[1]}: %{{customdata[1]}}<br>'
    ),
    customdata=filtered_data[columns_for_pairing].values,
    marker=dict(opacity=0)
)

# Update layout
fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    height=800,
    mapbox=dict(center=dict(lat=center_lat, lon=center_lon))
)

# Option to overlay first set of circles
overlay1 = st.sidebar.checkbox(f'Overlay {columns_for_pairing[0]} (orange)', value=True)
if overlay1:
    fig1 = px.scatter_mapbox(
        filtered_data,
        lat='latitude',
        lon='longitude',
        size=columns_for_pairing[0],
        color_discrete_sequence=['orange'],
        hover_name='tooltip_header',
        mapbox_style='carto-positron',
        zoom=5,
        opacity=0.4
    )

    # Add columns for pairing to customdata for the first set
    fig1.update_traces(
        hovertemplate=(
            '<b>%{hovertext}</b><br>' +
            f'{columns_for_pairing[0]}: %{{customdata[0]}}<br>' +
            f'{columns_for_pairing[1]}: %{{customdata[1]}}<br>'
        ),
        customdata=filtered_data[columns_for_pairing].values,
        marker=dict(opacity=0.6)
    )

    # Overlay the first set of circles
    for trace in fig1.data:
        fig.add_trace(trace)

# Option to overlay second set of circles
overlay2 = st.sidebar.checkbox(f'Overlay {columns_for_pairing[1]} (blue)')
if overlay2:
    fig2 = px.scatter_mapbox(
        filtered_data,
        lat='latitude',
        lon='longitude',
        size=columns_for_pairing[1],
        color_discrete_sequence=['blue'],
        hover_name='tooltip_header',
        mapbox_style='carto-positron',
        zoom=5,
        opacity=0.4
    )

    # Add columns for pairing to customdata for the second set
    fig2.update_traces(
        hovertemplate=(
            '<b>%{hovertext}</b><br>' +
            f'{columns_for_pairing[0]}: %{{customdata[0]}}<br>' +
            f'{columns_for_pairing[1]}: %{{customdata[1]}}<br>'
        ),
        customdata=filtered_data[columns_for_pairing].values,
        marker=dict(opacity=0.6)
    )

    # Overlay the second set of circles
    for trace in fig2.data:
        fig.add_trace(trace)

# Display the map
st.plotly_chart(fig, use_container_width=True)