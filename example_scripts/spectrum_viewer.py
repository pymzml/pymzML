#!/usr/bin/env python3

import sys
import os

import pymzml

import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html


print('loading run...')
run = pymzml.run.Reader(sys.argv[1])

all_ids = []
for spec_id, offset in run.info['offset_dict'].items():
    try:
        all_ids.append(int(spec_id))
    except:
        continue
FIRST_SPECTRUM_ID = min(all_ids)
LAST_SPECTRUM_ID = max(all_ids)

p = pymzml.plot.Factory()
p.new_plot()

tic_x=[]
tic_y=[]
for x,y in run['TIC'].peaks():
    tic_x.append(x)
    tic_y.append(y)
max_tic = max(tic_y)

tic_annotation = []

for n, RT in enumerate(tic_x):
    tic_annotation.append(
        'RT: {0:1.3f}<br>ID: {1}'.format(
            RT,
            all_ids[n]
        )
    )

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
        value=FIRST_SPECTRUM_ID,
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


def get_spectrum(spectrum_id):
    return run[spectrum_id]

def sanitize_id(spectrum_id_from_input):
    if spectrum_id_from_input not in [None, '']:
        spectrum_id  = int(spectrum_id_from_input)
    else:
        spectrum_id = FIRST_SPECTRUM_ID
    if spectrum_id < FIRST_SPECTRUM_ID:
        spectrum_id = FIRST_SPECTRUM_ID
    if spectrum_id > LAST_SPECTRUM_ID:
        spectrum_id = LAST_SPECTRUM_ID
    return spectrum_id


@app.callback(
    dash.dependencies.Output('tic-plot', 'figure'),
    [
        dash.dependencies.Input('spectrum-input-field', 'value'),
    ]
)
def update_TIC(spectrum_id_from_input=None):
    spectrum_id = sanitize_id(spectrum_id_from_input)
    spectrum = get_spectrum(spectrum_id)
    rt = spectrum.scan_time[0]
    figure = {
        'data':[
            {
                'x':tic_x,
                'y':tic_y,
                'line':{'color':'black'},
                'text':tic_annotation
            },
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
def trigger_new_spec_from_input( spectrum_id_from_input=None):
    spectrum_id = sanitize_id(spectrum_id_from_input)
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
        tmp_selected_precursors = spectrum.selected_precursors[0]
        format_str_template = '<br>'
        for key, format_template in [ ('mz',' Precursor m/z: {0}'), ('i', '; intensity {0:1.2e}'), ('charge','; charge: {0}') ]:
            if key in tmp_selected_precursors.keys():
                format_str_template += format_template.format(tmp_selected_precursors[key])
        title += format_str_template
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
