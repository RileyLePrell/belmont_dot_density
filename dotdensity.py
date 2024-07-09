import geopandas as gpd
import pandas as pd
import pydeck as pdk
import streamlit as st
import plotly.graph_objects as go

# Load shapefiles
shapefile_2010s = gpd.read_file("Shapefile_Final/merged_2010s.shp")
shapefile_2020s = gpd.read_file("Shapefile_Final/merged_2020s.shp")

# Concatenate shapefiles
merged_gdf = pd.concat([shapefile_2010s, shapefile_2020s])

# Rename columns
merged_gdf = merged_gdf.rename(columns={
    'Total Popu': 'Total Population',
    'White Popu': 'White Population',
    'Black Popu': 'Black Population',
    'Asian Popu': 'Asian Population',
    'Hispanic o': 'Hispanic or Latino Population',
    'Some other': 'Some other race'
})

# Create a DataFrame for dot density
def create_dot_density_df(gdf):
    dot_density_data = []
    for _, row in gdf.iterrows():
        for pop, color in zip(
            ['White Population', 'Black Population', 'Asian Population', 'Hispanic or Latino Population', 'Some other race'],
            ['#ffb262', '#129e56', '#e7298a', '#7570b3', '#43a8b5']
        ):
            count = row[pop] // 10  # One dot for every 10 people
            for _ in range(int(count)):
                centroid = row['geometry'].centroid
                dot_density_data.append({
                    'GEOID': row['GEOID'],
                    'Year': row['Year'],
                    'Color': color,
                    'Longitude': centroid.x,
                    'Latitude': centroid.y
                })
    return pd.DataFrame(dot_density_data)

dot_density_df = create_dot_density_df(merged_gdf)

# Define the colors for the demographic groups
colors = {
    'White Population': '#ffb262',
    'Black Population': '#129e56',
    'Asian Population': '#e7298a',
    'Hispanic or Latino Population': '#7570b3',
    'Some other race': '#43a8b5'
}

# Function to Create a Stacked Bar Chart of Racial %'s
def create_demographic_bar_chart(demographic_totals, year):
    fig = go.Figure()

    # Extract relevant data for the selected year
    year_data = demographic_totals[demographic_totals['Year'] == year]
    if year_data.empty:
        st.write(f"No data available for the year {year}")
        return None

    data = {
        'White Population': year_data['White Percentage'].values[0],
        'Black Population': year_data['Black Percentage'].values[0],
        'Asian Population': year_data['Asian Percentage'].values[0],
        'Hispanic or Latino Population': year_data['Hispanic Percentage'].values[0],
        'Some other race': year_data['Other Percentage'].values[0]
    }

    annotations = []
    cumulative_percent = 0

    # Bar Chart + Hover Functionality
    for i, (category, percentage) in enumerate(data.items()):
        fig.add_trace(go.Bar(
            x=[percentage],
            y=['Demographics'],
            name=category,
            orientation='h',
            marker=dict(color=colors[category]),
            hoverinfo='text',
            hovertext=f"{category}: {percentage:.1f}%"
        ))

        # Show percentages only if they are greater than 7%
        if percentage > 7:
            position = cumulative_percent + (percentage / 2)
            cumulative_percent += percentage
            annotations.append(dict(
                x=position,
                y=-0.1,
                text=f"{category}: {percentage:.1f}%",
                showarrow=False,
                font=dict(size=12),
                xref="x",
                yref="paper"
            ))

    # Making Bar's Stacked
    fig.update_layout(
        barmode='stack',
        title=f"Demographic Percentages for {year}",
        title_x=0.5,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        annotations=annotations,
        showlegend=False,
        height=300  
    )
    return fig

# Streamlit App
st.title("Mecklenburg County Interactive Dot Density Map")

# Slider for Year
year = st.slider("Select Year", min_value=int(merged_gdf['Year'].min()), max_value=int(merged_gdf['Year'].max()), step=1)

# Filter data by selected year
year_data = dot_density_df[dot_density_df['Year'] == year]

# Map Visualization with Pydeck
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=35.2271,
        longitude=-80.8431,
        zoom=10,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=year_data,
            get_position='[Longitude, Latitude]',
            get_fill_color='[Color[0], Color[1], Color[2], 140]',
            get_radius=20,
        ),
    ],
))

# Stacked Bar Chart for demographic percentages
demographic_columns = ['White Population', 'Black Population', 'Asian Population', 'Hispanic or Latino Population', 'Some other race', 'Total Population']
demographic_totals = merged_gdf[demographic_columns + ['Year']].groupby('Year').sum().reset_index()
demographic_totals['White Percentage'] = demographic_totals['White Population'] / demographic_totals['Total Population'] * 100
demographic_totals['Black Percentage'] = demographic_totals['Black Population'] / demographic_totals['Total Population'] * 100
demographic_totals['Asian Percentage'] = demographic_totals['Asian Population'] / demographic_totals['Total Population'] * 100
demographic_totals['Hispanic Percentage'] = demographic_totals['Hispanic or Latino Population'] / demographic_totals['Total Population'] * 100
demographic_totals['Other Percentage'] = demographic_totals['Some other race'] / demographic_totals['Total Population'] * 100

fig = create_demographic_bar_chart(demographic_totals, year)
if fig:
    st.plotly_chart(fig)
