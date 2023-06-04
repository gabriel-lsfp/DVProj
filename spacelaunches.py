# --------- NOVA IMS -----------
#  Digital Visualization Project
# --- Space Launch Statistics ---
# Mauro Camarinha 20170333
# Licínio Pereira 20221252

# imports
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

# Raw Data Load
TotalsByCountry = pd.read_excel('data/spacelaunches.xlsx', sheet_name='TotalsByCountry')
TotalsByCountry.fillna(0, inplace=True)

RawData = pd.read_excel('data/spacelaunches.xlsx', sheet_name='RawData')
# Remove future scheduled launches
RawData = RawData[RawData['Year'] < 2023]
data_filter = RawData

totals = pd.read_excel('data/spacelaunches.xlsx', sheet_name='TotalsByCountryYear')

# apply filter
totals = totals[totals['Year'] < 2023]
totals.fillna(0, inplace=True)

# create the filtered dataset
data_filter = totals.groupby(['Year']).agg(
    {'Total Launches': 'sum', 'Failure': 'sum', 'Successful': 'sum', 'Partial Failure': 'sum'}).reset_index(
    ['Year'])

print(data_filter.head(5).to_string())

# print(data_filter['Status'].iloc[1])
# print(TotalsByCountry.head(50).to_string())

#print(RawData['Status'])

status_options = ['Failure', 'Successful', 'Partial Failure']

mapbox_token = 'pk.eyJ1IjoibWNhbWFyaW5oYSIsImEiOiJjbGllcm5qNGYwbW5qM2RzMDFkeHlyemZrIn0.ZPA2E7nD2vGQ782y_9iEQA'
# define map data
data_scattermap = dict(type='scattermapbox',
                       lat=TotalsByCountry['Lat'],
                       lon=TotalsByCountry['Lon'],
                       name="",
                       mode="markers",
                       text=TotalsByCountry['Country'],
                       customdata=TotalsByCountry['Total Launches'],
                       marker=dict(color='steelblue',
                                   opacity=0.8,
                                   size=np.log2(TotalsByCountry['Total Launches']) * 5,
                                   sizemin=4
                                   ),
                       hovertext=(TotalsByCountry['Successful'] / TotalsByCountry['Total Launches']),
                       hovertemplate="<b>Country: </b> %{text} <br>" +
                                     "<b>Total Launches: </b> %{customdata} <br>"
                                     "<b>Success Rate: %{hovertext:.0%}",
                       )

layout_scattermap = dict(mapbox=dict(style='light',
                                     accesstoken=mapbox_token
                                     ),
                         autosize=False,
                         margin=dict(
                             l=0,
                             r=0,
                             b=0,
                             t=0
                         ),
                         paper_bgcolor='#9EDBDA',
                         hovermode='closest'
                         )

fig_scattermap = go.Figure(data=data_scattermap, layout=layout_scattermap)

# Construction of the App
app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([
    html.Div([
        html.Div([html.Label('Year:'),
                  dcc.RangeSlider(
                      id='date_range',
                      min=RawData['Year'].min(),
                      max=RawData['Year'].max(),
                      marks={i: '{}'.format(str(i)) for i in range(1960, 2040, 5)},
                      value=[1957, 2022],
                      tooltip={"placement": "bottom", "always_visible": True},
                      step=1
                      )],
                 className='column_two_filter'
                 ),
        html.Div([
                   dcc.Graph(
                        id='map',
                        figure=fig_scattermap
                   ),
                 ],
                  className='column_two_filter'
                 ),
             ],
              className='Box_1'
          ),

    html.Div([html.Label('Linha temporal de lançamentos')],
              className ='sub title'
             ),
    html.Div([
              dcc.Graph(id='time_line')], style={'margin-top': 20},
              className='grafico'
             ),
    html.Div([
              html.H1('Status of Space Launch'),
              dcc.Dropdown(
                    id='status_drop',
                    options=status_options,
                    value=['Successful'],
                    multi=True
              ),
             ],
               className='filter_box'
            ),
    html.Div(id='debug', style={'margin-top': 20})
])


@app.callback(
    Output('debug', 'children'),
    [Input('date_range', 'value')]
)
def update_debug(dates):
    if dates is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate

    return 'Year: [{:0.0f}, {:0.0f}]'.format(dates[0], dates[1])


@app.callback(
    Output('map', 'figure'),
    Input('date_range', 'value')
)
def update_map(years):
    if years is None:
        # PreventUpdate prevents ALL outputs updating
        raise dash.exceptions.PreventUpdate

    # get data
    totals = pd.read_excel('data/spacelaunches.xlsx', sheet_name='TotalsByCountryYear')

    # apply filter
    totals = totals[totals['Year'].between(years[0], years[1])]
    totals.fillna(0, inplace=True)

    totals_sum = totals.groupby(['Country', 'Lat', 'Lon']).agg(
        {'Total Launches': 'sum', 'Failure': 'sum', 'Successful': 'sum', 'Partial Failure': 'sum'}).reset_index(['Country', 'Lat', 'Lon'])

    # define map data
    data_scattermap = dict(type='scattermapbox',
                           lat=totals_sum['Lat'],
                           lon=totals_sum['Lon'],
                           name="",
                           mode="markers",
                           text=totals_sum['Country'],
                           customdata=totals_sum['Total Launches'],
                           marker=dict(color='steelblue',
                                       opacity=0.8,
                                       size=totals_sum['Total Launches'] / 10,
                                       sizemin=10
                                       ),
                           hovertext=(totals_sum['Successful'] / totals_sum['Total Launches']),
                           hovertemplate="<b>Country: </b> %{text} <br>" +
                                         "<b>Total Launches: </b> %{customdata} <br>"
                                         "<b>Success Rate: %{hovertext:.0%}",

                           )

    layout_scattermap = dict(mapbox=dict(style='light',
                                         accesstoken=mapbox_token,
                                         # Fix center
                                         # center=dict(lat=totals_sum['Lat'].iloc[5],
                                         #             lon=totals_sum['Lon'].iloc[5]
                                         #             )
                                        #zoom=0.8
                                        ),
                             autosize=True,
                             margin=dict(
                                 l=0,
                                 r=0,
                                 b=0,
                                 t=0
                             ),
                             paper_bgcolor='#9EDBDA',
                             hovermode='closest',
                             )

    return go.Figure(data=data_scattermap, layout=layout_scattermap)


    # grafico linha
    @app.callback(
        Output('time_line', 'figure'),
        Input('status_drop', 'value')
              )
    def update_lines(estados):
        if estados is None:
            # PreventUpdate prevents ALL outputs updating
            raise dash.exceptions.PreventUpdate

        # get data
        totais = pd.read_excel('data/spacelaunches.xlsx', sheet_name='TotalsByCountryYear')

    print("SSSSSSSS ...!")
    # apply filter
    totais = totais[totais['Year'] < 2023]
    totais.fillna(0, inplace=True)

    # create the filtered dataset
    data_filter = totais.groupby(['Year']).agg(
            {'Total Launches': 'sum', 'Failure': 'sum', 'Successful': 'sum', 'Partial Failure': 'sum'}).reset_index(
            ['Year'])

    # selecting the variables of each line
    status = estados

    layout_line = None
    data_line = []

    for status in variables:
        x_line = data_filter['Year']
        y_line = data_filter['Status']

   data_line.append(dict(type='scatter',
                        mode='lines',
                        x=data_filter['Year'],
                        y=data_filter[status],
                        text='',
                        customdata=status,
                        name=status,
                        hovertemplate="<b>Status: </b> %{customdata} <br>" +
                                      "<b>Year: </b> %{x} <br>" +
                                      "<b>Value: </b> %{y} <br>"))

   layout_line = dict(xaxis=dict(title='Year'),
                   yaxis=dict(title='Status'),
                   legend=dict(
                   orientation="h"
          ),
          margin=dict(
              l=40,
              r=40,
              b=20,
              t=5
          ),
          paper_bgcolor='#9EDBDA')

    return go.Figure(data=data_line, layout=layout_line)


if __name__ == '__main__':
    app.run_server(debug=True)
