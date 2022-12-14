import base64
import datetime
import io
from dash import dcc, html, Input, Output, State, dash_table
import dash
import dash_bootstrap_components as dbc
# from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
# import dash_core_components as dcc
# import dash_html_components as html
# import dash_table
import numpy as np
import pandas as pd


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = 'Pricelist Import Prep'
app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or Select Files'
        ],
        id='uploadedContent'
        ),
        style={
            'width': '70%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px 15%'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), header=0)
            df.columns = ['Serial','Name','Price','Warranty','Old_Name','Weight','LB']
            df['Price'] = np.where(df['Exchange'] == "Core Exchange/Flat Rate", (df['Price']/2)+500, df['Price'])

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), header=None)
            df.columns = ['Serial','Name','Price','Warranty','Old_Name','Weight','LB']
            df['Price'] = np.where(df['Warranty'] == "Core Exchange/Flat Rate", (df['Price']/2)+500, df['Price'])

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            export_headers='none',
            export_format='xlsx'
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback([Output('output-data-upload', 'children'),Output('uploadedContent','children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        
        return children, list_of_names

    else:
        raise PreventUpdate



if __name__ == '__main__':
    app.run_server(debug=False)



