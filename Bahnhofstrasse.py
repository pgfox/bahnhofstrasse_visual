import dash
import dash.dcc as dcc
import dash_bootstrap_components as dbc
import dash.html as html
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from itertools import chain
from DataHelper import DataManager

import logging
logging.basicConfig(level=logging.DEBUG)

LOG = logging.getLogger("Bahnhofstrasse_vis")
fh = logging.FileHandler('logs/Bahnhofstrasse_vis.log')
fh.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)

LOG.addHandler(ch)
LOG.addHandler(fh)


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'bahnofstasse_pedestrians.com'

data_manager = DataManager()

COLOR_PALETTE = ['#203c3b', '#447270', '#6b9493', '#F6E271', '#F6b915']


def default_fig_layout(fig):
    fig.update_layout(
        width=900,
        height=600,
        font=dict(
            family="Open Sans",
            size=14,
            color=COLOR_PALETTE[1],
        ),
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=3,
            ticks='outside',
            tickfont=dict(
                family="Open Sans",
                size=12,
                color=COLOR_PALETTE[1],
            ),
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=True,
            showline=True,
            showticklabels=True,
            rangemode="tozero",
            tickfont=dict(
                family="Open Sans",
                size=12,
                color=COLOR_PALETTE[1],
            ),
        ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=False,
        plot_bgcolor='white',
       
    )

    return fig


breakdown_card = dbc.Card(
    [
        dbc.CardHeader(
            dcc.Tabs(
                [

                    #dcc.Tab(label="Bahnhofstrasse (Nord)", id="Bahnhofstrasse (Nord)", value="Bahnhofstrasse (Nord)", className="my-tab-one", selected_className='custom-tab-selected'),
                    dcc.Tab(label="Bahnhofstrasse (Mitte)", id="Bahnhofstrasse (Mitte)", value="Bahnhofstrasse (Mitte)", className="my-tab-one",selected_className='custom-tab-selected'),
                    dcc.Tab(label="Bahnhofstrasse (Süd)", id="Bahnhofstrasse (Süd)", value="Bahnhofstrasse (Süd)", className="my-tab-one",selected_className='custom-tab-selected')

                ],
                id="card-tabs", value="Bahnhofstrasse (Mitte)",
                className="card-header"
            )
        ),
        dbc.CardBody(dcc.Graph(id="card_graph", figure={}, config={
                'displayModeBar': False
            }))
    ],className="top-card"
)


@app.callback(
    Output("card_graph", "figure"), [Input("card-tabs", "value"),
                                     Input("radio_button", "value")]
    
)
def update_fig_4_1(selected_data,radio_button_value):
      
    df = data_manager.location_date_time_last_year().reset_index()

    location = selected_data
    
    df = df[df["location_name"] == location]
    df = df.set_index('month', drop=False)

    fig = go.Figure()

    if (location == 'Bahnhofstrasse (Mitte)') & (radio_button_value == 'children' ):
        fig.update_layout(title="December afternoons had the most child pedestrians.<br> Child pedestrians counts were much smaller than adult pedestrian counts.")
    elif (location == 'Bahnhofstrasse (Mitte)') & (radio_button_value != 'children' ):
        fig.update_layout(title="December afternoons had the most pedestrians.")
    elif  (location == 'Bahnhofstrasse (Süd)') & (radio_button_value == 'children') :
        fig.update_layout(title="Afternoons were the busiest, but Bahnhofstrasse (Mitte) <br> has almost double the pedestrian counts. <br> Child pedestrians counts were much smaller than adult pedestrian counts.")
    elif  (location == 'Bahnhofstrasse (Süd)') & (radio_button_value != 'children') :
        fig.update_layout(title="Afternoons were the busiest, but Bahnhofstrasse (Mitte) <br> had almost double the pedestrian counts.")    
    else:
        fig.update_layout(title=" ")
     
    
    fig.update_layout(title_x=0.5, title_y=.95, title_xanchor='center', title_yanchor='top')

    if(radio_button_value == 'children'):
        column_to_use = 'child_pedestrians_count'    
    elif (radio_button_value == 'adults'):
        column_to_use = 'adult_pedestrians_count' 
    else:
        column_to_use = 'pedestrians_count'


    #interate over all times of day
    for time_of_day in ['Night','Morning','Afternoon','Evening']:

        time_of_day_df = df[df["time_of_day"] == time_of_day]
        if time_of_day == 'Afternoon':
            color = COLOR_PALETTE[3]
        else:
            color = COLOR_PALETTE[1]
    
    
        fig.add_trace(go.Scatter(x=time_of_day_df["month_year"], y=time_of_day_df[column_to_use],
                             name=time_of_day,
                             line=dict(color=color, width=4),
                             connectgaps=True,
                             ))

        fig.add_annotation(xref='paper', x=1, y=time_of_day_df.at['September', column_to_use],
                        xanchor='left', yanchor='middle',
                        text=f' {time_of_day}',
                        font=dict(family="Open Sans",
                                  color=COLOR_PALETTE[1],
                                  size=16),
                        showarrow=False)
        
    
    fig = default_fig_layout(fig)


    if  radio_button_value == 'children':
        yaxis_range_value=[0, 20_000]  
    else:
        yaxis_range_value=[0, 800_000]
    
    fig.update_layout( width=800, height=750, yaxis_tickformat=".2s",yaxis_range=yaxis_range_value)
    fig.update_layout(margin=dict(l=100, r=180, t=150, b=150))

    fig.update_xaxes(title_text='Months')
    fig.update_yaxes(title_text='Pedestrian count')

    return fig


def make_fig_detections_by_location():
    location_totals_df = data_manager.count_by_location_last_year().reset_index()

    
    fig = px.bar(location_totals_df,
                 x="location_name",
                 y="pedestrians_count",
                 color="location_name",
                 color_discrete_map={'Bahnhofstrasse (Süd)': COLOR_PALETTE[1],
                                     'Bahnhofstrasse (Mitte)': COLOR_PALETTE[3],

                                     }
                )
    
    fig.update_traces(hovertemplate='%{y} <br> pedestrians detected in test %{x}')

    fig.update_layout(margin=dict(l=150, r=180, t=100, b=50))
    fig.update_layout(title_x=0.45, title_y=.95, title_xanchor='center', title_yanchor='top')

    fig.update_layout(showlegend=False, plot_bgcolor='white',
                      width=900,
                      height=500,
                      font=dict(
                          family="Open Sans",
                          size=14,
                          color=COLOR_PALETTE[1],
                      ),
                      xaxis=dict(
                         
                          showspikes=True,
                          spikethickness=1,
                          linecolor='rgb(204, 204, 204)',
                          linewidth=3,
                          ticks='outside',
                          title="",
                          tickfont=dict(
                              family="Open Sans",
                              size=12,
                              color=COLOR_PALETTE[1],
                          ),
                          #range=[0, 20000000]
                      ),
                      yaxis=dict(
                          tickformat=".3s",
                          title="",
                          tickfont=dict(
                              family="Open Sans",
                              size=12,
                              color=COLOR_PALETTE[1],
                          ),

                      ),
                      hovermode="closest",
                      hoverlabel=dict(
                          bgcolor="white",
                          font_family="Open Sans",
                          font_size=12,
                          font_color=COLOR_PALETTE[1],
                      )
                      )

    fig.update_xaxes(title_text='Location')
    fig.update_yaxes(title_text='Pedestrian count')
    
    return fig
    



def make_fig_detections_by_month():
    df = data_manager.count_by_month_last_year().reset_index()
    LOG.debug(df.head())

  

   
    fig = px.bar(df,
                 x="month_year",
                 y="pedestrians_count",
                 color="month",
                 color_discrete_map={'October': COLOR_PALETTE[0],
                                     'November': COLOR_PALETTE[0],
                                     "December": COLOR_PALETTE[3],
                                     "January": COLOR_PALETTE[0],
                                     "February": COLOR_PALETTE[0],
                                     "March": COLOR_PALETTE[0],
                                     "April": COLOR_PALETTE[0],
                                     "May": COLOR_PALETTE[0],
                                     "June": COLOR_PALETTE[0],
                                     "July": COLOR_PALETTE[3],
                                     "August": COLOR_PALETTE[0],
                                     "September": COLOR_PALETTE[0]
                                     }
                )

    fig.update_traces(hovertemplate='%{y} <br> pedestrians detected in %{x}')

    fig.update_layout(margin=dict(l=150, r=180, t=100, b=50))
    fig.update_layout(title="December and July are busiest months."),
    fig.update_layout(title_x=0.45, title_y=.95, title_xanchor='center', title_yanchor='top')

    fig.update_layout(showlegend=False, plot_bgcolor='white',
                      width=900,
                      height=500,
                      font=dict(
                          family="Open Sans",
                          size=14,
                          color=COLOR_PALETTE[1],
                      ),
                      xaxis=dict(
                          showspikes=True,
                          spikethickness=1,
                          linecolor='rgb(204, 204, 204)',
                          linewidth=3,
                          ticks='outside',
                          title="",
                          tickfont=dict(
                              family="Open Sans",
                              size=12,
                              color=COLOR_PALETTE[1],
                          ),
                          #range=[0, 20000000]
                      ),
                      yaxis=dict(
                          tickformat=".3s",
                          title="",
                          tickfont=dict(
                              family="Open Sans",
                              size=12,
                              color=COLOR_PALETTE[1],
                          ),

                      ),
                      hovermode="closest",
                      hoverlabel=dict(
                          bgcolor="white",
                          font_family="Open Sans",
                          font_size=12,
                          font_color=COLOR_PALETTE[1],
                      )
                      )
    
    fig.update_xaxes(title_text='Month')
    fig.update_yaxes(title_text='Pedestrian count')

    return fig


def flatten_list(list_of_lists):
    flatten_list = list(chain.from_iterable(list_of_lists))
    
    #insert NONE for every third step
    i = 2
    for x in range(0,12):
        flatten_list.insert(i,None)
        i=i+3
    
    return flatten_list

def make_dumb_bell():

    df_last = data_manager.count_by_month_last_year().reset_index()
    df_prev = data_manager.count_by_month_previous_year().reset_index()
    combined_df = pd.merge(df_prev,df_last, on='month')
    
    LOG.debug("make_dumb_bell - combined df:")
    LOG.debug(combined_df)
    
    
    # data twisting to get data for 'line' between points
    combined_df['line_values'] = combined_df[['pedestrians_count_x', 'pedestrians_count_y',]].values.tolist()
    combined_df['month_values'] = combined_df[['month', 'month']].values.tolist()
    list_of_lists_x = combined_df['line_values'].values.tolist()
    list_of_lists_y = combined_df['month_values'].values.tolist() 
    x_line_list = flatten_list(list_of_lists_x)
    y_line_list = flatten_list(list_of_lists_y)
    list_of_last_x = df_last['pedestrians_count'].values.tolist()
    list_of_previous_x = df_prev['pedestrians_count'].values.tolist()
    list_months = df_last['month'].values.tolist()
 
    
    fig = go.Figure(
    data=[
        
        go.Scatter(
            x=x_line_list,
            y=y_line_list,
            mode="markers+lines",
            showlegend=False,
            name="",
            hovertemplate=' ',
            marker=dict(
                symbol="arrow", 
                color=COLOR_PALETTE[0],
                size=10, 
                angleref="previous", 
                standoff=3
                
            )
        ), 
         
        go.Scatter(
            x=list_of_previous_x,
            y=list_months,
            mode="markers",
            name=" ",
            hovertemplate='%{y} (from previous 12 months) <br> pedestrians detected is %{x}',
            showlegend=True,
            marker=dict(
                color=COLOR_PALETTE[0],
                size=10
            )   
        ),
        
        go.Scatter(
            x=list_of_last_x,
            y=list_months,
            mode="markers",
            name=" ",
            hovertemplate='%{y} (from last 12 months) <br> pedestrians detected is %{x}',
            showlegend=True,
            marker=dict(
                color=COLOR_PALETTE[3],
                size=10
            )
            
        ),
        
       
        ]
    )
    
    fig.add_annotation(xref='paper', x=0.26, yref='paper', y=0.95,
                           xanchor='left', yanchor='middle',
                           text='Previous 12 months',
                           font=dict(family="Open Sans",
                                     color=COLOR_PALETTE[0],
                                     size=16),
                           showarrow=False)
    
    fig.add_annotation(xref='paper', x=0.63, yref='paper', y=0.95,
                           xanchor='left', yanchor='middle',
                           text='Last 12 months',
                           font=dict(family="Open Sans",
                                     color=COLOR_PALETTE[0],
                                     size=16),
                           showarrow=False)
    
    fig = default_fig_layout(fig)

    fig.update_layout(xaxis_range=[0, 3000000], xaxis_tickformat=".3s", yaxis={"mirror" : "allticks" } )
    fig.update_layout(margin=dict(l=100, r=180, t=150, b=50))

    fig.update_layout(title=" Trend: more pedestrians last year compared to the previous year. "),
    fig.update_layout(title_x=0.45, title_y=.95, title_xanchor='center', title_yanchor='top')

    #fig.update_traces(hovertemplate='%{y} <br> pedestrians detected in %{x}')
    fig.update_layout(hovermode="closest")    
    
    fig.update_layout(
        xaxis = dict(
        tickmode = 'array',
        tickvals = [0,1_000_000, 2_000_000, 3_000_000],
        ticktext = ['0','1M', '2M', '3M']
    )       
    )
    
    fig.update_xaxes(title_text='Pedestrian count')
    fig.update_yaxes(title_text='Month')
    

    return fig



def make_fig_3():
    df = data_manager.count_by_day_last_year().reset_index().reset_index()

  
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["pedestrians_count"],
                                 name="",
                                 line=dict(color=COLOR_PALETTE[3], width=4),
                                 connectgaps=True,
                                 marker_size=8,
                                 text=df['date'],
                                 hovertemplate='%{text}<br> pedestrians detected: %{y}' 
                                 ))
    
    
    fig = default_fig_layout(fig)

    fig.update_layout(margin=dict(l=100, r=180, t=100, b=150))
    fig.update_layout(
        title="Counts remain quite consistent through out the year <br> and appear to follow a weekly cycle."),
    fig.update_layout(title_x=0.45, title_y=.95, title_xanchor='center', title_yanchor='top')        
        
    fig.update_layout(
        width=900,
        height=750,
        xaxis_tickformat = '%d %B %Y',
        yaxis_tickformat = '.3s'
    )    
        
    # add labels to plot
    fig.add_annotation(xref='paper', x=0.54, yref='paper', y=0.48,
                           xanchor='left', yanchor='middle',
                           text='  Sächsilüüte',
                           font=dict(family="Open Sans",
                                     color=COLOR_PALETTE[1],
                                     size=16),
                           showarrow=False)

    
    fig.add_annotation(xref='paper', x=0.86, yref='paper', y=0.89,
                           xanchor='left', yanchor='middle',
                           text='   Street Parade',
                           font=dict(family="Open Sans",
                                     color=COLOR_PALETTE[1],
                                     size=16),
                           showarrow=False)
    
    
    fig.add_annotation(xref='paper', x=0.76, yref='paper', y=0.97,
                           xanchor='left', yanchor='middle',
                           text='   Züri Fäscht',
                           font=dict(family="Open Sans",
                                     color=COLOR_PALETTE[1],
                                     size=16),
                           showarrow=False)
    
    fig.update_xaxes(title_text='Date',tickangle=45)
    fig.update_yaxes(title_text='Pedestrian count')

    return fig


def make_violin():
    df =  data_manager.count_by_day_last_year().reset_index()
    
    LOG.debug("make_violin() - df: ")
    LOG.debug(df.head())

    
    fig = px.violin(df, y="pedestrians_count", x="day", box=False, 
                      color="day",
                      color_discrete_map={'Monday': COLOR_PALETTE[0],
                                          'Tuesday': COLOR_PALETTE[0],
                                          "Wednesday": COLOR_PALETTE[0],
                                          "Thursday": COLOR_PALETTE[0],
                                          "Friday": COLOR_PALETTE[0],
                                          "Saturday": COLOR_PALETTE[3],
                                          "Sunday": COLOR_PALETTE[0],                                          
                                          },   
          hover_data=df.columns)
    
    
    fig.update_xaxes(categoryorder='array', categoryarray= ['Monday','Tuesday','Wednesday','Thursday', 'Friday','Saturday','Sunday'])

    
    fig.update_traces(meanline_visible=True)
    
    fig.update_traces(hovertemplate='%{y} <br> pedestrians detected in %{x}')

    fig.update_layout(margin=dict(l=150, r=180, t=100, b=50))
    fig.update_layout(title="Saturday had more pedestrians."),
    fig.update_layout(title_x=0.45, title_y=.95, title_xanchor='center', title_yanchor='top')

    fig.update_layout(showlegend=False, plot_bgcolor='white',
                      width=900,
                      height=500,
                      font=dict(
                          family="Open Sans",
                          size=14,
                          color=COLOR_PALETTE[1],
                      ),
                      xaxis=dict(
                          tickformat=".3s",
                          showspikes=True,
                          spikethickness=1,
                          linecolor='rgb(204, 204, 204)',
                          linewidth=3,
                          ticks='outside',
                          title="",
                          tickfont=dict(
                              family="Open Sans",
                              size=12,
                              color=COLOR_PALETTE[1],
                          ),
                          #range=[0, 20000000]
                      ),
                      yaxis=dict(
                          title="",
                          tickfont=dict(
                              family="Open Sans",
                              size=12,
                              color=COLOR_PALETTE[1],
                          ),

                      ),
                      hovermode="closest",
                      hoverlabel=dict(
                          bgcolor="white",
                          font_family="Open Sans",
                          font_size=12,
                          font_color=COLOR_PALETTE[1],
                      )
                      )
    fig.update_layout(xaxis_tickformat=".2s", )
    
    fig.update_layout(hovermode="closest") 
    
    fig.add_annotation(x='Friday', y=65000,
            text="median ",
            xanchor="right",
            yanchor="bottom",
            showarrow=True,
            arrowhead=1)
    
    fig.update_xaxes(title_text='Day of week')
    fig.update_yaxes(title_text='Pedestrian count')

    return fig


def make_sunburst():
    df = data_manager.location_day_time_last_year().reset_index()
    
    fig = px.sunburst(df, path=['location_name','day','time_of_day'], values='pedestrians_count', width=800, height=800,
                      color="location_name",
                      color_discrete_map={"Bahnhofstrasse (Süd)": COLOR_PALETTE[3],
                                          "Bahnhofstrasse (Nord)": COLOR_PALETTE[3],
                                          "Bahnhofstrasse (Mitte)": COLOR_PALETTE[3]
                                          },
                      range_color=[0, 10])

    fig.update_traces(textinfo="label+percent parent")
    fig.update_traces(textfont=dict(family="Open Sans", color=COLOR_PALETTE[1]), selector=dict(type='sunburst'))

    fig.update_layout(
        font=dict(
            family="Open Sans",
            size=15,
            color=COLOR_PALETTE[1],
        ),
        xaxis=dict(
            tickformat=".3s",
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
        ),
        yaxis=dict(
            tickformat=".3s",
            showgrid=False,
            zeroline=True,
            showline=True,
            showticklabels=True,
            rangemode="tozero"
        ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=10,
            r=20,
            t=150,
        ),
        showlegend=False,
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_family="Open Sans",
            font_size=12,
            font_color=COLOR_PALETTE[1],
        )

    )

    fig.update_traces(hovertemplate='%{label}<br> pedestrian count: %{value:.3s} ')

    fig.update_layout(
        title=" Saturday afternoon had more pedestrians,<br> both in Bahnhofstrasse Süd and Mitte."),
    fig.update_layout(title_x=0.45, title_y=.95, title_xanchor='center', title_yanchor='top')

    return fig


def make_map():
    fig = go.Figure(go.Scattermapbox(
        mode = "markers",
        lon = [-73.605], lat = [45.51],
        marker = {'size': 30, 'color': ["cyan"]} ,visible='legendonly'))


    fig.update_layout(
        mapbox = {
            'style': "stamen-terrain",
            'center': { 'lon': 8.538115, 'lat': 47.373045},
            'zoom': 14.5, 'layers': [{
                'source': {
                    'type': "FeatureCollection",
                    'features': [{
                        'type': "Feature",
                        'geometry': {
                            'type': "MultiPolygon",
                            'coordinates': [[[                                                              
                                [8.538222, 47.374015], [8.538598, 47.374015], 
                                [8.538694, 47.374211], [8.538823, 47.374429], 
                                [8.538845, 47.374654], [8.539445, 47.375744], 
                                [8.539767, 47.376427], [8.540025, 47.376812], 
                                [8.539681, 47.376921], [8.539177, 47.375897], 
                                [8.538845, 47.375272], [8.538501, 47.374582], 
                                [8.538222, 47.374015]
                            ]]]
                        }
                    }]
                    
                },
                'type': "fill", 'below': "traces", 'color': COLOR_PALETTE[0]}, 
                
                {
                    'source': {
                        'type': "FeatureCollection",
                        'features': [{
                            'type': "Feature",
                            'geometry': {
                                'type': "MultiPolygon",
                                'coordinates': [[[
                                    [8.538947, 47.370233], [8.539215, 47.370273],
                                    [8.538936, 47.371039], [8.53863, 47.371879],
                                    [8.538453, 47.372373], [8.538405, 47.37315], 
                                    [8.538383, 47.373735], [8.538405, 47.373848], 
                                    [8.538099, 47.373811], [8.538099, 47.373753], 
                                    [8.538115, 47.373045], [8.538147, 47.372395], 
                                    [8.538244, 47.372108], [8.538587, 47.371148], 
                                    [8.538614, 47.371018], [8.53871, 47.370785], 
                                    [8.538796, 47.370633], [8.538947, 47.370233]
                                ]]]
                            }
                        }]
                        
                    },
                    'type': "fill", 'below': "traces", 'color': COLOR_PALETTE[3]},
                {
                    'source': {
                        'type': "FeatureCollection",
                        'features': [{
                            'type': "Feature",
                            'geometry': {
                                'type': "MultiPolygon",
                                'coordinates': [[[
                                     
                                    [8.539939, 47.367523], [8.540229, 47.367581],
                                    [8.540014, 47.368162], [8.539649, 47.369139],
                                    [8.539526, 47.369568], [8.539215, 47.369543],
                                    [8.539322, 47.369154], [8.539617, 47.368376], 
                                    [8.539939, 47.367523]
                                    
                                    
                                ]]]
                            }
                        }]
                        
                    },
                    'type': "fill", 'below': "traces", 'color': COLOR_PALETTE[1]}
                
                ]},
        margin = {'l':50, 'r':200, 'b':50, 't':50},showlegend=False)

 
    fig.add_annotation(xref='paper', x=1.00, yref='paper', y=0.70,
                            xanchor='left', yanchor='middle',
                            text='   Nord',
                            font=dict(family="Open Sans",
                                      color=COLOR_PALETTE[0],
                                      size=25),
                            showarrow=False)
    
    
    fig.add_annotation(xref='paper', x=1.00, yref='paper', y=0.50,
                            xanchor='left', yanchor='middle',
                            text='   Mitte',
                            font=dict(family="Open Sans",
                                      color=COLOR_PALETTE[3],
                                      size=25),
                            showarrow=False)
    
    fig.add_annotation(xref='paper', x=1.00, yref='paper', y=0.20,
                            xanchor='left', yanchor='middle',
                            text='   Süd',
                            font=dict(family="Open Sans",
                                      color=COLOR_PALETTE[1],
                                      size=25),
                            showarrow=False)

    fig.update_layout(showlegend=False, plot_bgcolor='white',
                       width=800,
                       height=700,
                       font=dict(
                           family="Open Sans",
                           size=16,
                           color=COLOR_PALETTE[1],
                       ))    
   

    return fig


 
'''
Layout of the HTML page

'''


card_3 = dbc.Card(
    [
        dbc.CardBody(html.Div([
            html.Span(["Saturday"], className="summary-graphic"),
            "  was the most popular day with pedestrians on Bahnhofstrasse in the last 12 months"],
            className="summary-text")
        )
    ],className="summary-text, summary-card"
)

card_1 = dbc.Card(
    [
        dbc.CardBody(html.Div(["Bahnhofstrasse (Mitte) had almost ",
            html.Span(["twice"], className="summary-graphic"),
            "  as many pedestrians as Bahnhofstrasse (Süd) in the last 12 months"], className="summary-text")
        )
    ],className="summary-text, summary-card"
)

card_4 = dbc.Card(
    [
        dbc.CardBody(html.Div([
            html.Span(["Afternoons"], className="summary-graphic"),
            "  were consistently most popular with pedestrians in the last 12 months",
        ], className="summary-text")
        )
    ],className="summary-text, summary-card"
)

card_2 = dbc.Card(
    [
        dbc.CardBody(html.Div([ "The last 12 months had ",
            html.Span(["more"], className="summary-graphic"),
            "  pedestrians than in the previous 12 months", ], className="summary-text")
        )
    ],className="summary-text, summary-card"
)



#Actual Page layout

app.layout = html.Div([
    dbc.Row(
        [

            dbc.Col(html.Div([html.Br(), html.Br(), html.Br(), html.Br(),
                              html.Div([
                                  "13.5 Million pedestrians were counted on Zurich's Bahnhofstrasse (Mitte)",
                                  html.Br(),
                                  " in the last 12 months"], className="t1-heading")
                              ], className="container-fluid", style={'text-align': 'center'}),
                    width={'size': 12, "offset": 0, 'order': 1}),
        ]
    ),
    
    
    dbc.Row(
        [
            dbc.Col(html.Div([html.Br(), html.Br(), html.Br(),
                              "As part of a joint pilot project involving the international real estate consulting company CBRE,",
                              " the PropTech company hystreet.com, Swiss Life Asset Managers, Zurich Urban Development and  ",
                              "the Zurich Bahnhofstrasse Association, Hystreet is collecting pedestrian frequencies on Bahnhofstrasse.",
                              " Bahnhofstrasse has been segmented into sections and laser scanners are used to detect pedestrians in each section. The counts are updated on an hourly basis."

                              ], className="container-fluid"), width={'size': 4, "offset": 4, 'order': 1}),

        ]
    ),
    
    dbc.Row(
        [

            dbc.Col(html.Div([html.Br(), html.Br(),
                              "In the last 12 months, how many pedestrians were counted in each Bahnhofstrasse section?",
                              ], className="my-subtitle", style={'text-align': 'center'}),
                    width={'size': 12, "offset": 0}),

        ]
    ),
    dbc.Row(
        [html.Div([html.Br(), html.Br()])
         ]),
    
    dbc.Row(
        [

            dbc.Col(dcc.Graph(id='fig_0_5', figure=make_fig_detections_by_location(), config={
                'displayModeBar': False
            }),
                    width=6, lg={'size': 5, "offset": 0, 'order': 1}
                    ),
            dbc.Col(html.Div([
                html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), 
                html.Span(["Hint: "], className="explain-title"),
                ("Hover over graphs for details"),
                html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
                html.Span(["Last 12 months: "], className="explain-title"),
                ("1st October 2022 until 30th September 2023"),
            ], className="hint-format"), width={'size': 2, "offset": 2, 'order': 0}),
        ]
    ),
    
    dbc.Row(
        [

            dbc.Col(html.Div([html.Br(), html.Br(), html.Br(), html.Br(),
                              "Where exactly is Bahnhofstrasse (Mitte) located?",
                              ], className="my-subtitle", style={'text-align': 'center'}),
                    width={'size': 12, "offset": 0, 'order': 1}),

        ]
    ),
    dbc.Row(
        [
            dbc.Col(html.Div([html.Br(), html.Br(), html.Br(),
                              " This visualization uses data from Bahnhofstrasse (Mitte) and (Süd): ",
                              " data for Bahnhofstrasse (Nord) is incomplete." 

                              ], className="container-fluid"), width={'size': 4, "offset": 4, 'order': 1}),

        ]
    ),
    dbc.Row(
        [
            dbc.Col(html.Div([html.Br(), html.Br(),
                              ], className="container-fluid"), width={'size': 4, "offset": 4, 'order': 1}),

        ]
    ),
    dbc.Row(
        [

            dbc.Col(dcc.Graph(id='fig_3_6', figure=make_map(), config={
                'displayModeBar': False
            }),
                 
                   width={"size": 6, "offset": 0, "order":1},
                    ),
            dbc.Col(html.Div([
                html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),html.Br(), html.Br(),
                html.Span(["Hint: "], className="explain-title"),
                ("Scroll over map to zoom in/out"),
            ], className="hint-format"), width={'size': 2, "offset": 2, 'order': 0}),

        ]
    ),
    
    dbc.Row(
        [

            dbc.Col(
                    html.Div([
                        html.Div([html.Br(), html.Br(),
                              "In the last 12 months, how many pedestrians were counted each month?",
                              ], className="my-subtitle", style={'text-align': 'center'}),
                    
                        html.Div([
                                      "(Bahnhofstrasse Süd and Mitte combined)",
                                      ], className="container-fluid", style={'text-align': 'center'}),
                    ], className="my-subtitle", style={'text-align': 'center'}),
                    
                    width={'size': 12, "offset": 0}),

        ]
    ),
    dbc.Row(
        [html.Div([html.Br(), html.Br()])
         ]),
    dbc.Row(
        [

            dbc.Col(html.Div([
                
            ], className="container-fluid"), width={'size': 4, "offset": 4, 'order': 1}),

        ]
    ),
    
    
    dbc.Row(
        [

            dbc.Col(dcc.Graph(id='fig_1', figure=make_fig_detections_by_month(), config={
                'displayModeBar': False
            }),
                    width=6, lg={'size': 5, "offset": 0, 'order': 1}
                    ),
            dbc.Col(html.Div([
                html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),html.Br(), html.Br(),
                html.Span(["Hint: "], className="explain-title"),
                ("Hover over graphs for details"),
            ], className="hint-format"), width={'size': 2, "offset": 2, 'order': 0}),
        ]
    ),
    dbc.Row(
        [html.Div([html.Br(), html.Br(), html.Br(), html.Br()])
         ]),
    dbc.Row(
        [
           
            dbc.Col(
                
            html.Div([
                html.Div([html.Br(), html.Br(),
                       "How does the last 12 month pedestrian counts compare to the previous 12 months counts?",
                      ], className="my-subtitle", style={'text-align': 'center'}),
            
                html.Div([
                              "(Bahnhofstrasse Süd and Mitte combined)",
                              ], className="container-fluid", style={'text-align': 'center'}),
            ], className="my-subtitle", style={'text-align': 'center'}),
            
            width={'size': 12, "offset": 0}),

        ]
    ),
    dbc.Row(
        [
            dbc.Col(html.Div([html.Br(), html.Br(),
                              ], className="container-fluid"), width={'size': 4, "offset": 4, 'order': 2}),
        ]
    ),
    dbc.Row(
        [

            dbc.Col(dcc.Graph(id='fig_2', figure=make_dumb_bell(), config={
                'displayModeBar': False
            }),
                    width=6, lg={'size': 5, "offset": 0, 'order': 1}
                    ),
            dbc.Col(html.Div([
                html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
                html.Span(["Previous 12 months: "], className="explain-title"),
                (" 1st October 2021 to 30th September 2022"),
                html.Br(),html.Br(), html.Br(),
                html.Span(["Last 12 months: "], className="explain-title"),
                (" 1st October 2022 to 30th September 2023")
               
            ], className="container-fluid"), width={'size': 2, "offset": 2, 'order': 0}),
        ]
    ),
    dbc.Row(
        [html.Div([html.Br(), html.Br(), html.Br(), html.Br()])
         ]),
    dbc.Row(
        [

            dbc.Col(
                
            html.Div([
                html.Div([html.Br(), html.Br(),
                       "In the last 12 months, how many pedestrians were counted per day?",
                      ], className="my-subtitle", style={'text-align': 'center'}),
            
                html.Div([
                              "(Bahnhofstrasse Süd and Mitte combined)",
                              ], className="container-fluid", style={'text-align': 'center'}),
            ], className="my-subtitle", style={'text-align': 'center'}),
            
            width={'size': 12, "offset": 0}),

        ]
    ),
    dbc.Row(
        [
            dbc.Col(html.Div([html.Br(), html.Br(),
                              ], className="container-fluid"), width={'size': 4, "offset": 4, 'order': 1}),

        ]
    ),
    dbc.Row(
        [

            dbc.Col(
                dcc.Graph(id='fig_3', figure=make_fig_3(), config={
                    'displayModeBar': False
                    })
                , width=6, lg={'size': 8, "offset": 0, 'order': 1}
            ),
            dbc.Col(html.Div([
                html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),html.Br(), html.Br(),
                html.Span(["Hint: "], className="explain-title"),
                ("Hover over graphs for details"),
            ], className="hint-format"), width={'size': 2, "offset": 2, 'order': 0}),

        ]
    ),

    dbc.Row(
        [

            dbc.Col(
               
             html.Div([
                 html.Div([html.Br(), html.Br(),
                        "In the last 12 months, which day of the week was most popular with pedestrians?",
                       ], className="my-subtitle", style={'text-align': 'center'}),
             
                 html.Div([
                               "(Bahnhofstrasse Süd and Mitte combined)",
                               ], className="container-fluid", style={'text-align': 'center'}),
             ], className="my-subtitle", style={'text-align': 'center'}),
             
             width={'size': 12, "offset": 0,'order': 1}),

           

        ]
    ),
    dbc.Row(
        [
            dbc.Col(html.Div([html.Br(), html.Br(),
                              ], className="container-fluid"), width={'size': 4, "offset": 4, 'order': 1}),

        ]
    ),
    dbc.Row(
        [

            dbc.Col(dcc.Graph(id='fig_3_5', figure=make_violin(), config={
                'displayModeBar': False
            }),
                    width=6, lg={'size': 8, "offset": 0, 'order': 1}
                    ),

             dbc.Col(html.Div([
                 html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),html.Br(), html.Br(),
                 html.Span(["Hint: "], className="explain-title"),
                 ("Hover over graphs for details"),
             ], className="hint-format"), width={'size': 2, "offset": 2, 'order': 0}),
        ]
    ),
   
        

    dbc.Row(
        [

            dbc.Col(html.Div([html.Br(), html.Br(), html.Br(), html.Br(),
                              "In the last 12 months, which day and 'times of day'",html.Br(),
                              " had biggest portion of pedestrians?",
                              ], className="my-subtitle", style={'text-align': 'center'}),
                    width={'size': 12, "offset": 0, 'order': 1}),

        ]
    ),

    dbc.Row(
        [
            html.Div([html.Br(), html.Br()])
        ]
    ),

    dbc.Row(
        [
        dbc.Col(html.Div([
            
                html.Br(), html.Br(),html.Br(),html.Br(),
                html.Div([html.Span(["Hint: "], className="explain-title"),
                ("Click on Inner Circle and Middle Ring to expand. Hover over plot segments to get actual pedestrian counts")], className="hint-format"),
                html.Br(), html.Br(), html.Br(),
                 html.Span(["Inner Circle: "], className="explain-title"),
                ("Section of Bahnhofstrasse"),
                html.Br(), html.Br(),
                 html.Span(["Middle Ring: "], className="explain-title"),
                ("Days of week"),
                html.Br(), html.Br(),
                 html.Span(["Outer Ring: "], className="explain-title"),
                ("Time of day"),
                 html.Br(),
             
               
            ], className="container-fluid"), width={'size': 2, "offset": 1, 'order': 0}),

            dbc.Col(dcc.Graph(id='fig_4', figure=make_sunburst(), config={
                'displayModeBar': False
            },
                              style={
                                  "padding-left": "200px",
                              }
                              ),
                    width=6, lg={'size': 5, "offset": 0, 'order': 1}
                    ),
            
        ]
    ),
    dbc.Row(
        [
            dbc.Col(
                html.Div([html.Span(["Night: "], className="explain-title"),
                          ("from 00:01 until 06:00"),
                    ], className="container-fluid"), width={'size': 2, "offset": 3, 'order': 1}),
            
            dbc.Col(
                html.Div([ html.Span(["Morning: "], className="explain-title"),
                          ("from 06:01 until 12:00"),
                    ], className="container-fluid"), width={'size': 2, "offset": 0, 'order': 2}),
            
            dbc.Col(
                html.Div([ html.Span(["Afternoon: "], className="explain-title"),
                (
                    "from 12:01 until 18:00"),
                    ], className="container-fluid"), width={'size': 2, "offset": 0, 'order': 3}),
            
            dbc.Col(
                html.Div([  html.Span(["Evening: "], className="explain-title"),
                 ("from 18:01 until 24:00"),
                    ], className="container-fluid"), width={'size': 2, "offset": 0, 'order': 4}),
        ]),
    
    dbc.Row(
        [
            html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
        ]),
    dbc.Row(
        [
            dbc.Col(html.Div([
                "In the last 12 months, what time was busiest in each month?",
            ], className="my-subtitle", style={'text-align': 'center'}), width={'size': 12, "offset": 0, 'order': 1}),
        ]
    ),
    dbc.Row(
        [
            html.Br(), html.Br(), html.Br(), html.Br(),
        ]),
    dbc.Row(
        [
           
            dbc.Col(
                
                html.Div(
                    [    
                        html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),html.Br(), html.Br(),
                        html.Span(["Hint: "], className="explain-title"),
                        ("Switch between locations and toggle between count of total/adult/child pedestrians"),
                        html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
                        html.Br(),
                        dcc.RadioItems(
                             options={
                                 'both': ' Adults & Children',
                                 'adults': ' Adults',
                                 'children': ' Children'
                                 },
                             id="radio_button", value='both'
                    )], className="container-fluid", style={'text-align': 'left', 'color':COLOR_PALETTE[1] }
                         ), 
                width={'size': 2, "offset": 2, 'order': 1}
                
            ),
           
           
           
            dbc.Col(html.Div([
                breakdown_card
            ],className="container-fluid", style={'text-align': 'center'}), width={'size': 5, "offset": 0, 'order': 2}),

        ]
                ),

    dbc.Row(
        [
            html.Br(), html.Br(), html.Br(), html.Br(),
        ]),

    dbc.Row(
        [
            dbc.Col(html.Div([
                "Key Points",
            ], className="my-subtitle", style={'text-align': 'center'}), width={'size': 12, "offset": 0, 'order': 1}),
        ]
    ),
    dbc.Row(
        [
            html.Br(), html.Br(),
        ]),
    
     dbc.Row(
         [
             dbc.Col(
                 card_1,
                 width={'size': 6, "offset": 3, 'order': 0}),
             html.Br(), html.Br(),

         ]
     ),
     dbc.Row(
         [
             dbc.Col(
                 card_2, 
                 width={'size': 6, "offset": 3, 'order': 0}),
             html.Br(), html.Br(),

         ]
     ),
     dbc.Row(
         [
             dbc.Col(
                 card_3, 
                 width={'size': 6, "offset": 3, 'order': 0}),
             html.Br(), html.Br(),
             
         ]
     ),
     dbc.Row(
         [
             dbc.Col(
                 card_4, 
                 width={'size': 6, "offset": 3, 'order': 0}),
             html.Br(), html.Br(),
             
             
         ]
     ),

    dbc.Row(
        [
            dbc.Col(html.Div([html.Br(), html.Br(), html.Br(), html.Br(),
                              html.A("Source: opendata.swiss - Passantenfrequenzen an der Bahnhofstrasse - Stundenwerte", 
                                     href='https://opendata.swiss/de/dataset/passantenfrequenzen-an-der-bahnhofstrasse-stundenwerte ', target="_blank",
                                     className="container-fluid"),
                              #])        
                              html.Br(),
                              html.Br(),
                              ]
                             ), width={'size': 4, "offset": 4, 'order': 2}
                    )
        ]
    )
],
    className="dbc"
)

if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(debug=False)
