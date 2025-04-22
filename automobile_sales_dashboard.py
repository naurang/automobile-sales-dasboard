#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Load the data using pandas
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')
#print(data.columns)
# Initialise the Dash app

app = dash.Dash(__name__, external_stylesheets=[
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
    "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap",
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
])

# this line of code needed to load the server
server = app.server



# Year list
year_list = [i for i in range(1980, 2024)]

# Layout
app.layout = html.Div(style={'fontFamily': 'Roboto, sans-serif', 'backgroundColor': '#f8f9fa', 'padding': '20px'}, children=[
    html.Div(className="container", children=[
        html.H1("📊 Automobile Sales Statistics Dashboard", className="text-primary mb-4"),
        html.Div(id="kpi-container", className="row text-center mb-4"),


html.Div(className="row text-center mb-4", children=[
    html.Div(className="col-md-3", children=[
        html.Div(className="card text-white bg-primary mb-3", children=[
            html.Div(className="card-body", children=[
                html.H5("Total Vehicles Sold", className="card-title"),
                html.H3(f"{int(data['Automobile_Sales'].sum()):,}", className="card-text")
            ])
        ])
    ]),
    html.Div(className="col-md-3", children=[
        html.Div(className="card text-white bg-secondary mb-3", children=[
            html.Div(className="card-body", children=[
                html.H5("Total Ad Expenditure", className="card-title"),
                html.H3(f"${int(data['Advertising_Expenditure'].sum()):,}", className="card-text")
            ])
        ])
    ]),
    html.Div(className="col-md-3", children=[
        html.Div(className="card text-white bg-success mb-3", children=[
            html.Div(className="card-body", children=[
                html.H5("Highest Sales Year", className="card-title"),
                html.H3(data.groupby('Year')['Automobile_Sales'].sum().idxmax(), className="card-text")
            ])
        ])
    ]),
    html.Div(className="col-md-3", children=[
        html.Div(className="card text-white bg-info mb-3", children=[
            html.Div(className="card-body", children=[
                html.H5("Top Vehicle Type", className="card-title"),
                html.H3(data.groupby('Vehicle_Type')['Automobile_Sales'].sum().idxmax(), className="card-text")
            ])
        ])
    ])
]),


        html.Div(className="row mb-4", children=[
            html.Div(className="col-md-6", children=[
                html.Label("Select Statistics:", className="form-label fw-bold"),
                dcc.Dropdown(
                    id='dropdown-statistics',
                    options=[
                        {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                        {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
                    ],
                    placeholder="Select a report type",
                    className="form-select"
                )
            ]),
            html.Div(className="col-md-6", children=[
                html.Label("Select Year:", className="form-label fw-bold"),
                dcc.Dropdown(
                    id='select-year',
                    options=[{'label': i, 'value': i} for i in year_list],
                    placeholder="Select year",
                    className="form-select"
                )
            ])
        ]),

        html.Div(id='output-container', className='row gy-4'),
                # 👇 ADD YOUR DETAILS HERE 
        html.Footer(className="text-center mt-5", children=[
            html.Hr(),
            html.P([
                "Dashboard by ",
                html.A("Suraj Singh", href="https://www.linkedin.com/in/suraj-singh-naurang/", target="_blank", className="text-decoration-none fw-bold text-primary"),
                html.I(className="bi bi-linkedin ms-2")
            ], className="text-muted")
        ])

    ])
])

# Callback: Disable year dropdown if "Recession" is selected
@app.callback(
    Output('select-year', 'disabled'),
    Input('dropdown-statistics', 'value')
)
def update_year_availability(stat):
    return stat != 'Yearly Statistics'

@app.callback(
    Output('kpi-container', 'children'),
    [Input('dropdown-statistics', 'value'), Input('select-year', 'value')]
)
def update_kpis(stat_type, year):
    if stat_type == 'Recession Period Statistics':
        filtered = data[data['Recession'] == 1]
    elif stat_type == 'Yearly Statistics' and year:
        filtered = data[data['Year'] == year]
    else:
        return []

    total_sales = int(filtered['Automobile_Sales'].sum())
    total_ad = int(filtered['Advertising_Expenditure'].sum())
    top_type = filtered.groupby('Vehicle_Type')['Automobile_Sales'].sum().idxmax()
    avg_sales = round(filtered.groupby('Month')['Automobile_Sales'].mean().mean(), 2)

def kpi_card(title, value, icon, color):
    # Format numbers with comma; prefix currency symbol only for specific KPIs
    if "Ad" in title:
        formatted_value = f"${value:,}"
    else:
        formatted_value = f"{value:,}" if isinstance(value, (int, float)) else value

    return html.Div(className="col-md-3", children=[
        html.Div(className=f"card text-white bg-{color} mb-3 shadow", children=[
            html.Div(className="card-body", children=[
                html.H5([html.I(className=f"me-2 {icon}"), title], className="card-title"),
                html.H3(formatted_value, className="card-text")
            ])
        ])
    ])



    return [
        kpi_card("Total Vehicles Sold", total_sales, "bi bi-speedometer2", "primary"),
        kpi_card("Total Ad Expenditure", total_ad, "bi bi-currency-dollar", "secondary"),
        kpi_card("Top Vehicle Type", top_type, "bi bi-truck-front-fill", "success"),
        kpi_card("Avg. Sales per Month", avg_sales, "bi bi-bar-chart", "info")
    ]


# Callback: Update graphs
@app.callback(
    Output('output-container', 'children'),
    [Input('dropdown-statistics', 'value'), Input('select-year', 'value')]
)
def update_output(stat, year):
    charts = []

    if stat == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]

        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        unempl = recession_data.groupby(['Vehicle_Type', 'unemployment_rate'])['Automobile_Sales'].mean().reset_index()

        charts = [
            dcc.Graph(figure=px.line(yearly_rec, x='Year', y='Automobile_Sales',
                                     title="Average Automobile Sales During Recession")),
            dcc.Graph(figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales',
                                    title="Avg. Vehicles Sold by Type (Recession)")),
            dcc.Graph(figure=px.pie(exp_rec, names='Vehicle_Type', values='Advertising_Expenditure',
                                    title="Ad Spend by Vehicle Type (Recession)")),
            dcc.Graph(figure=px.bar(unempl, x='Vehicle_Type', y='Automobile_Sales', color='unemployment_rate',
                                    title="Impact of Unemployment on Sales by Type"))
        ]
    elif stat == 'Yearly Statistics' and year:
        yearly_data = data[data['Year'] == year]
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        monthly_sales = data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()

        charts = [
            dcc.Graph(figure=px.line(yas, x='Year', y='Automobile_Sales',
                                     title="Average Automobile Sales (All Years)")),
            dcc.Graph(figure=px.line(monthly_sales, x='Month', y='Automobile_Sales',
                                     title="Total Monthly Sales")),
            dcc.Graph(figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
                                    title=f"Avg. Sales by Vehicle Type ({year})")),
            dcc.Graph(figure=px.pie(exp_data, values='Advertising_Expenditure', names='Vehicle_Type',
                                    title=f"Ad Spend by Type ({year})"))
        ]

    return [html.Div(className="col-md-6", children=[chart]) for chart in charts]
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
