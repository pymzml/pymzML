#!/usr/bin/env python3

from __future__ import print_function

import sys
import os

import pymzml

import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html


print('loading run...')
run = pymzml.run.Reader(sys.argv[1])

p = pymzml.plot.Factory()
p.new_plot()

tic_x=[]
tic_y=[]
for x,y in run['TIC'].peaks():
    tic_x.append(x)
    tic_y.append(y)
max_tic = max(tic_y)


app = dash.Dash(__name__)


app.layout = html.Div([
    dcc.Graph(
        id='spectrum-plot',
        style={
            'fontFamily': 'Helvetica',
        }
    ),
    html.H3(
        children='Please specify spectrum ID',
        style={
            'fontFamily': 'Helvetica',
        }
    ),
    dcc.Input(
        id='spectrum-input-field',
        value=1,
        type='text',
        style={
            'width': '20%',
            'height': '30px',
            'lineHeight': '30px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'fontFamily': 'Helvetica',
            'fontSize': '130%'
        }
    ),
    dcc.Graph(
        id='tic-plot',
    ),
])

spectra_buffer = {}

def get_spectrum(spectrum_id):
    if spectrum_id not in spectra_buffer.keys():
        spectrum  = run[spectrum_id]
        spectra_buffer[spectrum_id] = spectrum
    else:
        spectrum = spectra_buffer[spectrum_id]
    return spectrum


@app.callback(
    dash.dependencies.Output('tic-plot', 'figure'),
    [
        dash.dependencies.Input('spectrum-input-field', 'value'),
    ]
)
def update_TIC(spectrum_id_from_input=None):
    if spectrum_id_from_input not in [None, '']:
        spectrum_id  = int(spectrum_id_from_input)
    else:
        spectrum_id = 1
    if spectrum_id > run.info['spectrum_count']:
        spectrum_id = run.info['spectrum_count']
    spectrum = get_spectrum(spectrum_id)
    rt = spectrum.scan_time[0]
    figure = {
        'data':[
            {'x':tic_x, 'y':tic_y, 'line':{'color':'black'}},
            {
                'x':[rt, rt],
                'y':[0,max_tic],
                'line':{'color':'red', 'width':2}, 
                'text':[
                    '',
                    'RT: {0}<br>ID: {1}'.format(
                        rt,
                        spectrum_id
                    )
                ]
            }
        ],
        'layout':go.Layout(
            xaxis={ 'title': 'RT', 'autorange':False, 'range':[0,max(tic_x)]},
            yaxis={'title': 'Intensity',},
            margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            showlegend=False,
            title = 'TIC'
        )
    }
    return figure


@app.callback(
    dash.dependencies.Output('spectrum-plot', 'figure'),
    [
        dash.dependencies.Input('spectrum-input-field', 'value'),
    ]
)
def trigger_new_spec_from_slider( spectrum_id_from_input=None):
    if spectrum_id_from_input not in [None, '']:
        spectrum_id  = int(spectrum_id_from_input)
    else:
        spectrum_id = 1
    # print(type(spectrum_id))
    if spectrum_id > run.info['spectrum_count']:
        spectrum_id = run.info['spectrum_count']
    spectrum = get_spectrum(spectrum_id)
    return update_figure(spectrum)



def update_figure(spectrum):
    spectrum_plot = p.add(
        spectrum.peaks('centroided'),
        color = ( 0, 0, 0 ),
        style = 'sticks',
        name = 'peaks'
    )
    new_spectrum_plot={}
    new_spectrum_plot['x'] = spectrum_plot['x'] 
    new_spectrum_plot['y'] = spectrum_plot['y']
    new_spectrum_plot['line']={'color':'black'}
    # print(spectrum_plot)
    title = 'Spectrum {0} @ RT: {1} [{2}s] of run {3}'.format(
        spectrum.ID,
        spectrum.scan_time[0],
        spectrum.scan_time[1],
        os.path.basename(sys.argv[1])
    )
    if spectrum.ms_level == 2:
        title += '<br> Precursor m/z: {mz} (intensity {i:1.2e}, charge: {charge})'.format(
            **spectrum.selected_precursors[0]
        )
    return {
        'data': [new_spectrum_plot],
        'layout': go.Layout(
            xaxis={ 'title': 'm/z'},
            yaxis={'title': 'Intensity',},
            margin={'l': 40, 'b': 40, 't': 80, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            title = title
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
