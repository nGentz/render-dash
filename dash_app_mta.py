import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd
from shapely.geometry import Point, Polygon
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Read csv file to pd dataframe
df = pd.read_csv('MTA_Subway_Hourly_Ridership__Beginning_February_2022.csv')

by_station_df = df.groupby(['station_complex_id', 'station_complex', 'borough', 'latitude', 'longitude'])['ridership'].sum().reset_index()

by_station_df['ridership_per_day'] = (by_station_df['ridership'] / 533).round(0)

# Specify your Mapbox access token (replace 'YOUR_MAPBOX_TOKEN' with your actual token)
mapbox_token = 'pk.eyJ1Ijoibmlja2dlbnR6IiwiYSI6ImNsMnE4MXBqYTFodWozamt6Y3UzaDN2bm8ifQ.sudv6WDuPydt3LtqMLJZlw'

by_station_df['scaled_marker_size'] = (by_station_df['ridership_per_day'] / by_station_df['ridership_per_day'].max() * 9).round(4)

by_station_df['station_complex'] = by_station_df['station_complex'].str.replace(r'\([^()]*\)', '')

by_station_df['locked_marker_size'] = 1

bins = [161.55, 10000, 50000, 75000, 135546]
bin_labels = [
    'Low (161 - 10000)',
    'Medium (10,000 - 50,000)',
    'High (50,000 - 75,000)',
    'Very High (75,000+)'
]

bin_colors = {
    'Low (161 - 10000)': 'rgb(255, 195, 0)',
    'Medium (10,000 - 50,000)': 'rgb(255, 87, 51)',
    'High (50,000 - 75,000)': 'rgb(199, 0, 57)',
    'Very High (75,000+)': 'rgb(88, 24, 69)'
}

by_station_df['ridership_bin'] = pd.cut(by_station_df['ridership_per_day'], bins=bins, labels=bin_labels)

by_station_df = by_station_df.sort_values(by=['ridership_per_day'], ascending=False).reset_index(drop=True)

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H4("Interactive Ridership by Station Map", style={'padding-left': '5%'}),  # Add left padding to the H4 title
    dcc.Checklist(
        id='marker-size-toggle',
        options=[
            {'label': 'Use scaled markers', 'value': 'scaled_marker_size'}
        ],
        value=[],
        style={'padding-left': '5%'},  # Add left padding to the checklist
    ),
    dcc.Graph(id='scatter-plot', style={'height': '800px'}),  # Adjust the height as needed
])

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('marker-size-toggle', 'value')]
)
def update_marker_size(selected_values):
    use_scaled_marker_size = 'scaled_marker_size' in selected_values

    hover_data = ['ridership_per_day', 'ridership', 'station_complex']
    hover_template = (
        "<b>Station</b>: %{customdata[2]}<br>"
        "<b>Ridership per Day</b>: %{customdata[0]}<br>"
        "<b>Ridership</b>: %{customdata[1]}"
    )

    fig = px.scatter_mapbox(
        by_station_df,
        lat='latitude',
        lon='longitude',
        color='ridership_bin',
        hover_name='station_complex',
        custom_data=[
            by_station_df['ridership_per_day'],
            by_station_df['ridership'],
            by_station_df['station_complex']
        ],
        size='scaled_marker_size' if use_scaled_marker_size else None,
        color_discrete_map=bin_colors
    )

    fig.update_layout(
        mapbox=dict(
            accesstoken=mapbox_token,
            style='mapbox://styles/mapbox/dark-v10',
            center=dict(lat=40.7128, lon=-74.0060),
            zoom=10.2,
        ),
        hovermode='closest',
    )

    fig.update_traces(hovertemplate=hover_template)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
