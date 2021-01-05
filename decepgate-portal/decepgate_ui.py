
''' Dashboard for  uploading and broadcasting honeyd config fileas to remote server and 
    show the live traffic of honeyd detections from the embedded device '''

import flask
import os
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
import dash_table_experiments as dt
import pandas as pd
from collections import OrderedDict
from datetime import datetime
import time
import base64
import io
import matplotlib.cm as cm
import numpy as np
import dash_cytoscape as cyto
import subprocess
import re
import socket
import fcntl
import struct
import calendar
import sys
import argparse

''' Logic for swapping config file and retain logs based on respective config files '''
conf_file=""
conf_pre_file=""
conf_data=""
csv_file=""



''' Default dummy config file '''
fp = open("./data-log.csv","a+")
fp.seek(0)
i_data=fp.read()
if len(i_data) == 0:
    fp.write("TimeStamp,Protocol,Src_Ip,Dest_Ip,Src_Port,Dest_Port\n")
fp.close()


if len(conf_data) == 0:
    data = pd.read_csv(
        './data-log.csv'
    )
else:
    conf_file=conf_data
    csv_file="./"+conf_file
    data = pd.read_csv(
        csv_file
    )

''' Sort Latest data '''
df = data.sort_values('TimeStamp', ascending=False)

X = []
Y = []
A = []
B = []
M = []
N = []
L=[]


def line_scatter(temp):
    '''Line scatter graph calculation for live feed'''
    groups = temp.groupby(by=['Dest_Ip','TimeStamp'])

    n=[]
    l=[]
    m=[]
    dt = datetime.now()
    
    timestamp = time.mktime(dt.timetuple()) + dt.microsecond / 1e6
    timestamp_h = timestamp - 60
    t_object = datetime.fromtimestamp(timestamp)
    t_obj = datetime.fromtimestamp(timestamp_h)

    ''' Grouping data based on time period '''
    for i,k in groups:
        time_obj = datetime.strptime(i[1],'%Y-%m-%d-%H:%M:%S.%f')
        timestamp_dup = calendar.timegm(time_obj.timetuple())+ time_obj.microsecond / 1e6
        if timestamp_dup >= timestamp_h and timestamp_dup <= timestamp:
            n.append(i[0])
            l.append(i[1])
            m.append(len(k))

    data = OrderedDict({'TimeStamp':l,'Dest_Ip':n, 'Count':m})

    ''' Create DataFrame '''
    dz = pd.DataFrame(data)
    
    ''' Data Formation for graph '''
    groups = dz.groupby(by=['Dest_Ip'])
    y=[]
    z=[]
    c=[]
    for i,k in groups:
        e=[]
        r=[]
        t=0
        ''' Picking last one minute live data ''' 
        for p in range(0,12):
            time_t=timestamp-t
            t=t+5
            timestamp_h = timestamp - t
            a=0
            for l in k['TimeStamp']:
                time_obj = datetime.strptime(l,'%Y-%m-%d-%H:%M:%S.%f')
                timestamp_dup = calendar.timegm(time_obj.timetuple())+ time_obj.microsecond / 1e6
                if timestamp_dup >= timestamp_h and timestamp_dup <= time_t:
                    a=a+1


            e.append(p+1)
            r.append(a)
        for q in range(0,12):
            y.append(i)
            z.append(e[q])
            c.append(r[q])

    return y,z,c

M,N,L=line_scatter(df)

dup = pd.DataFrame({'Devices':M ,
                   'Incomings':L,
                   'Time':N})

groups = dup.groupby(by='Devices')

ys=list(set(dup['Devices']))

colors = cm.rainbow(np.linspace(0, 1, len(ys)))


def bar_stat_ip(temp):
  '''Bar stat calculation for live feed'''
  n=[]
  l=[]
  a= list(temp['Dest_Ip'])
  d={}
  t=0
  ''' Data fromation for Bar chart '''
  d={i:a.count(i) for i in a}
  for i,k in sorted(d.items(), key=lambda x: x[1],reverse=True):
    n.append(i)
    l.append(k)
    t=t+1
    ''' Maximum of 5 devices with highest hit '''
    if t == 5:
      break
  return n,l

X,Y=bar_stat_ip(df)

def get_ip_address(ifname):
    '''TO get ip addrees based on interface'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s',ifname[:15].encode('utf-8'))
    )[20:24])

base_elements=[]


def network_topology():
    '''To create network topology based on config uploaded'''
    filePath = './demo.conf'
    try:
        with open(filePath,'r') as f:
            lines = f.readlines()
    except IOError as e:
        print("Config file yet to be created")
        n=[]
        return n  
    tpl=[]
    ifc=" "
    ''' Chunk the config file for parsing '''
    for i in lines:
        if "honeyd" in i :
            m=i.split("-i")
            v=m[1].split(" ")
            ifc=v[1]
            continue
        tpl.append(i)

    inc=0
    tpl_data={}
    for i in tpl:
        tpl_data[inc]=i.split(" ")
        inc=inc+1
    
    core={}

    h_device=" "
    h_conn=[]
    h_dev=[]
    entry=0
    fil_d=[]

    ''' Parsing config file to map topology '''
    for i,k in tpl_data.items():
        if len(k) <= 2:
            continue
        if k[1] == "entry":
            h_device=k[2].rstrip()
            entry=1
            continue
        if k[0] == "bind":
            device={}
            device['ip']=k[1].rstrip()
            device['name']=k[2].rstrip()
            h_dev.append(device)
            continue
        else:
            if k[1] == h_device and k[2] == "link":
                continue
            if k[2] == "add":
                if k[5].rstrip() not in fil_d:
                    route={}
                    route['s_ip']=k[1].rstrip()
                    route['d_ip']=k[5].rstrip()
                    fil_d.append(k[5].rstrip())
                    h_conn.append(route)
    
    fil_d.append(h_device)
    node_elements=[]

    ''' Map the parsed data to form topology '''
    if entry == 1:
        a={}
        buf = "EMBEDDED:HONEYD(%s)" % (h_device)
        a['data']={}
        a['data']['id']=h_device.rstrip()
        a['data']['label']=buf
        node_elements.append(a)
    else:
        dev=ifc
        a={}
        buf = "EMBEDDED:HONEYD(%s)" % (dev)
        a['data']={}
        a['data']['id']=dev.rstrip()
        a['data']['label']=buf
        node_elements.append(a)
    
    ''' mapping node and edge of the network '''
    edge_elements=[]
    basic_elements=[]
    for i in h_dev:
        a={}
        buf = "%s(%s)" % (i['name'].rstrip(),i['ip'].rstrip())
        a['data']={}
        a['data']['id']=i['ip'].rstrip()
        a['data']['label']=buf
        node_elements.append(a)
        if entry != 1:
            buf="%s-%s" %(i['ip'],dev)
            edge={}
            edge['data']={}
            edge['data']['id']=buf
            edge['data']['source']=i['ip'].rstrip()
            edge['data']['target']=dev
            buf="Edge from %s to %s" %(i['ip'].rstrip(),dev)
            edge['data']['label']=buf
            edge_elements.append(edge)
            continue
        if i['ip'] in fil_d:
            continue
        for j in fil_d:
            d_cmp = j.rsplit('.', 1)
            if d_cmp[0] in i['ip']:
                buf="%s-%s" %(i['ip'].rstrip(),j.rstrip())
                edge={}
                edge['data']={}
                edge['data']['id']=buf
                edge['data']['source']=i['ip'].rstrip()
                edge['data']['target']=j.rstrip()
                buf="Edge from %s to %s" %(i['ip'].rstrip(),j.rstrip())
                edge['data']['label']=buf
                edge_elements.append(edge)

    for i in h_conn:
        edge={}
        buf = "%s-%s" % (i['d_ip'].rstrip(),i['s_ip'].rstrip())
        edge['data']={}
        edge['data']['id']=buf
        edge['data']['source']=i['d_ip'].rstrip()
        edge['data']['target']=i['s_ip'].rstrip()
        buf="Edge from %s to %s" %(i['d_ip'].rstrip(),i['s_ip'].rstrip())
        edge['data']['label']=buf
        edge_elements.append(edge)

    basic_elements.extend(node_elements)
    basic_elements.extend(edge_elements)
    return basic_elements

base_elements=network_topology()


''' Dashboard style elements '''
app_colors = {
    'background': '#FFBB0A',
    'text': '#000000',
    'sentiment-plot': '#41EAD4',
    'volume-bar': '#FBFC74',
    'someothercolor': '#FF206E',
}

app = dash.Dash(__name__)

app.css.append_css({
    "external_url": "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
})

app.css.append_css({
    "external_url": 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

app.scripts.append_script({
    "external_url": "https://code.jquery.com/jquery-3.2.1.min.js"
})

app.scripts.append_script({
    "external_url": "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"
})


styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(88vh - 115px)'}
}

''' GUI Layout configuration '''
app.layout = html.Div(
        [
            html.Div(children=[
                # Column: Line Chart
                html.Div([
                        html.H4('Network Topology', style={'color': "#000000", 'width': 'auto','marginLeft': 10}),
                        cyto.Cytoscape(
                        id='cytoscape',
                            elements=base_elements,
                            layout={
                            'name': 'circle',
                            },
                        style={
                            'height': '60vh',
                            'width': '100%'
                        },
                        stylesheet=[
                        {
                            'selector': 'node',
                            'style': {
                                'background-color':'#2874A6',
                                "font-size": "10px",
                                'label': 'data(label)'
                                }
                        },
                        {
                            'selector': '[label *= "EMBEDDED"]',
                            'style': {
                                'background-color': '#F4D03F',
                                "font-size": "10px",
                                'shape': 'rectangle'
                            }
                        },
                        {
                            'selector': '[label *= "HONEYD"]',
                            'style': {
                                'background-color': '#17202A',
                                "font-size": "10px",
                                'shape': 'triangle'
                            }
                        }

                        ])

                        ], className="col-md-4",style={'backgroundColor':'#F7FBFE','border': 'thin lightgrey dashed', 'padding': '6px 0px 0px 8px','width':'50%','height': '650'}),
                    html.Div([
                    html.H4('Incoming Traffic', style={'color': "#000000", 'width': 'auto','marginLeft': 35}),
                    dcc.Graph(id='live-graph', animate=False, style={'width': 'auto'}),
                    dcc.Graph(id='live-bar', animate=False, style={'width': 'auto'}),
                    ], className="col-md-4",style={'backgroundColor':'#F7FBFE','border': 'thin lightgrey dashed', 'padding': '6px 0px 0px 8px', 'width':'50%','height': '650'}),
                ], className="row"),

            html.Div(className="row", children=[
                html.Div([
                html.H4('Log Stats', style={'color': "#000000", 'width': 'auto','align':'center'}),
                dt.DataTable(
                    rows=df.to_dict('records'),

                    #optional - sets the order of columns 
                    columns=df.columns,
                    max_rows_in_viewport=5,
                    sortable=True,
                    selected_row_indices=[],
                    id='live-table'
                    ),
                ], className="col-md-4", style={'width': '48%', 'display': 'inline-block'}),
            html.Div([  
                 html.H4('    Upload Config and Deploy', style={'color': "#000000", 'width': 'auto','marginLeft': 10}), #file upload tab
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                #Allow multiple files to be uploaded 
                multiple=True
            ),
            html.Div(id='output-data-upload'), # form design
            html.Form([
                dcc.Input(name='name'),
                html.Button('Submit', type='submit'),
                ], style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10,'width': '30%', 'display': 'inline-block'},action='/post', method='post')
            ],className="col-md-4", style={'marginLeft': 20, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10,'width': '47%', 'display': 'inline-block'})]), 
            dcc.Interval(
                id='graph-update',
                interval=5 * 1000  # in millisecond 1*1000= 1 second
                ),
            ]

)

@app.server.route('/post', methods=['POST'])
def on_post():
    ''' To broadcast uploaded config file '''
    data = flask.request.form
    n=data.get("name")
    data=n.split(",")
    for i in data:
        buf = "nc %s 8083 < ./demo.conf" % (i)
        print(buf)
        t=subprocess.call(buf, shell=True)
        if t != 0:
            print(t)
            return flask.redirect('/')
        else:
            fp = open("config.txt","w+") #to preserve the data file name
            fp.seek(0)
            fp.write(conf_file)
            fp.close()
    return flask.redirect('/')


@app.callback(Output('live-table', 'rows'),  # selected_row_indices'),
              [Input('graph-update', 'n_intervals')])
def update_table(n_intervals):
    ''' Live update of graph '''
    if len(conf_file) == 0:
        data = pd.read_csv(
            './data-log.csv'
        )
    else:
        csv_file="./"+conf_file
        data = pd.read_csv(
            csv_file
        )

    temp_2 = data.sort_values('TimeStamp', ascending=False)
    return temp_2.to_dict('records')


@app.callback(
    Output('live-bar', 'figure'),
    [Input('graph-update', 'n_intervals')])
def update_figure(n_intervals):
    ''' live update of bar chart '''
    if len(conf_file) == 0:
        data = pd.read_csv(
            './data-log.csv'
        )
    else:
        csv_file="./"+conf_file
        data = pd.read_csv(
            csv_file
        )

    temp2 = data.sort_values('TimeStamp', ascending=False)
    ''' Mark the plot '''
    X, Y = bar_stat_ip(temp2)
    trace0 = go.Bar(
    x=X,
    y=Y,
    marker=dict(
        color='rgb(158,202,225)',
        line=dict(
            color='rgb(8,48,107)',
            width=1.5,
        )
    ),
    opacity=0.6
    )

    data = [trace0]
    layout = go.Layout(
        title='Traffic Stats',
        margin={'l': 10, 'b': 40, 't': 40, 'r': 10},
        width=630,
        height=270,
        xaxis=dict(
            title='Devices',
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='Number of Hits',
            titlefont=dict(
                size=16,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=14,
                color='rgb(107, 107, 107)'
            )
        ),
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


    
def parse_contents_1(contents, filename, date):
    ''' Parse the config file contents '''
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    n=decoded.decode('utf-8')
    global conf_file
    conf_file=filename+".csv"
    global csv_file
    csv_file="./"+conf_file
    fp = open(conf_file,"a+")
    fp.seek(0)
    i_data=fp.read()
    if len(i_data) == 0:
        fp.write("TimeStamp,Protocol,Src_Ip,Dest_Ip,Src_Port,Dest_Port\n")
    fp.close()
    fp = open(conf_pre_file,"w+")
    fp.seek(0)
    fp.write(conf_file)
    fp.close()
    with open("demo.conf",'w+') as fp: # demo.conf is the config file uploaded
        fp.write(n)
        fp.write("\n")
    fp.close()
    return html.Div([

    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    ''' Toplogy update based on config upload '''
    if list_of_contents is not None:
        children = [
            parse_contents_1(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        global base_elements
        base_elements=network_topology()
        return children


@app.callback(Output('cytoscape', 'elements'),
        [Input('graph-update', 'n_intervals')])
def update_nodes(n_intervals):
    ''' Live update on topology '''
    return base_elements

@app.callback(Output('live-graph', 'figure'),
        [Input('graph-update', 'n_intervals')])
def update_graph_scatter(n_intervals):
    ''' Live update on graph '''
    if len(conf_file) == 0:
        temp_1 = pd.read_csv(
            './data-log.csv'
        )
    else:
        csv_file="./"+conf_file
        temp_1= pd.read_csv(
            csv_file
        )

    temp = temp_1.sort_values('TimeStamp', ascending=False)
    M,N,L=line_scatter(temp)
    dup = pd.DataFrame({'Devices':M ,
                   'Incomings':L,
                   'Time':N})

    groups = dup.groupby(by='Devices')

    ys=list(set(dup['Devices']))

    colors = cm.rainbow(np.linspace(0, 1, len(ys)))
    ''' Mark the topology '''
    data_1 = []
    for group, dataframe in groups:
        dataframe = dataframe.sort_values(by=['Time'])
        trace = go.Scatter(x=dataframe.Time.tolist(),
                       y=dataframe.Incomings.tolist(),
                       marker=dict(color=colors[len(data_1)]),
                       name=group)
        data_1.append(trace)

    layout =  go.Layout(xaxis={'title': 'Time'},
                    yaxis={'title': 'Traffic'},
                    margin={'l': 10, 'b': 40, 't': 40, 'r': 10},
                    width=630,
                    height=280,
                    hovermode='closest')

    figure = go.Figure(data=data_1, layout=layout)
    return figure






if __name__ == '__main__':

    ''' Pasre Command line arguments '''
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port",
                        nargs='?',help="Specify the name of a listening port ")
    parser.add_argument("-ip", "--ip",
                        nargs='?',
                        help="Specify a ip of the host")

    args = parser.parse_args()

    if not args.port:
        port=8050
    else:
        port=int(args.port)
    if not args.ip:
        ip='0.0.0.0'
    else:
        ip=str(args.ip)

    conf_pre_file = "config_pre.txt"

    '''File for preserving file name of data'''
    fp = open(conf_pre_file,"a+")
    fp.seek(0)
    conf_data=fp.read()
    fp.close()
    

    app.run_server(host=ip, port=port,debug=True)

