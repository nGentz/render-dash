import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# read csv
df = pd.read_csv('/Users/nickgentz/Downloads/dash_app/by_station_df.csv')

# Specify your Mapbox access token (replace 'YOUR_MAPBOX_TOKEN' with your actual token)
mapbox_token = 'pk.eyJ1Ijoibmlja2dlbnR6IiwiYSI6ImNsMnE4MXBqYTFodWozamt6Y3UzaDN2bm8ifQ.sudv6WDuPydt3LtqMLJZlw'

bin_colors = {
    'Low (161 - 10000)': 'rgb(255, 195, 0)',
    'Medium (10,000 - 50,000)': 'rgb(255, 87, 51)',
    'High (50,000 - 75,000)': 'rgb(199, 0, 57)',
    'Very High (75,000+)': 'rgb(88, 24, 69)'
}

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
        df,
        lat='latitude',
        lon='longitude',
        color='ridership_bin',
        hover_name='station_complex',
        custom_data=[
            df['ridership_per_day'],
            df['ridership'],
            df['station_complex']
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
