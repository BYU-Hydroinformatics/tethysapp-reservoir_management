#This is the main python script where your html content is created. search for tethys gizmos online for more information on gizmos
#Each page has its own function and code that is run for that specific page. Each html page needs its own function

import datetime
import plotly.graph_objs as go
import os
import pandas as pd

from django.shortcuts import render, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.contrib.sites.shortcuts import get_current_site


from tethys_sdk.gizmos import *
from tethys_sdk.permissions import has_permission

from model import getforecastflows, gethistoricaldata, getrecentdata, forecastdata, forecastlevels, gettabledates
from .app import ReservoirManagement as app

sites = ['Chacuey','Hatillo','Jiguey','Maguaca','Moncion','Rincon','Sabaneta','Sabana Yegua','Tavera-Bao','Valdesia']

def config(x):
    return {
        'Chacuey':{
	        'comids':['1396'],
	        'min_level':47.00,
	        'max_level':54.63,
	        'ymin':30,
	        'custom_history_name':False
	        },
        'Hatillo':{
	        'comids':['834', '813', '849', '857'],
	        'min_level':70.00,
	        'max_level':86.50,
	        'ymin':55,
	        'custom_history_name':False
	    },
        'Jiguey':{
	        'comids':['475', '496'],
	        'min_level':500.00,
	        'max_level':541.50,
	        'ymin':450,
	        'custom_history_name':False
	    },
        'Maguaca':{
	        'comids':['1399'],
	        'min_level':46.70,
	        'max_level':57.00,
	        'ymin':30,
	        'custom_history_name':False
	    },
        'Moncion':{
	        'comids':['1148','1182'],
	        'min_level':223.00,
	        'max_level':280.00,
	        'ymin':180,
	        'custom_history_name':False
	    },
        'Rincon':{
	        'comids':['853','922'],
	        'min_level':108.50,
	        'max_level':122,
	        'ymin':95,
	        'custom_history_name':False
	    },
        'Sabaneta':{
	        'comids':['863','862'],
	        'min_level':612,
	        'max_level':644,
	        'ymin':580,
	        'custom_history_name':False
	    },
        'Sabana Yegua':{
	        'comids':['593','600','599'],
	        'min_level':358,
	        'max_level':396.4,
	        'ymin':350,
	        'custom_history_name':"S. Yegua"
	    },
        'Tavera-Bao':{
	        'comids':['1024', '1140', '1142', '1153'],
	        'min_level':300.00,
	        'max_level':327.50,
	        'ymin':270,
	        'custom_history_name':"Tavera"
	    },
        'Valdesia':{
	        'comids':['159'],
	        'min_level':130.75,
	        'max_level':150.00,
	        'ymin':110,
	        'custom_history_name':False
	    }
    }.get(x, {})

def gen_urls(request):
	current_site = get_current_site(request)
	site_urls = list(map((lambda x: {
		'name':x,
		'url':request.build_absolute_uri('//' + str(current_site) + '/apps/reservoir-management/'+x.replace(" ","_")+'/'),
		'active':x in request.path
		}
	), sites))
	return site_urls

def edit_passthrough(request,button_to_show):
	#Can Set output data. Only allowed for admins
	if(has_permission(request, 'update_data')):
		return button_to_show;
	else:
		return False;

@login_required()
def home(request):
    return render(request, 'reservoir_management/home.html', {
        'site_urls':gen_urls(request),
        'show_edit':has_permission(request, 'update_data')
        })


@login_required()
def site_handler(request,site_name):
    """
    Main controller for the dams page.
    """
    gen_urls(request)
    site_name = site_name.replace('_'," ")

    # Get config
    site_config = config(site_name);
    comids = site_config['comids'];
    forecasteddata = gettabledates(comids)

    historyname = site_name
    if(site_config['custom_history_name']):
    	historyname = site_config['custom_history_name'];

    data = gethistoricaldata(historyname)

    min_level = [[data[0][0], site_config['min_level']], [data[-1][0], site_config['min_level']]]
    max_level = [[data[0][0], site_config['max_level']], [data[-1][0], site_config['max_level']]]

    timeseries_plot = TimeSeries(
        height='500px',
        width='500px',
        engine='highcharts',
        title=site_name,
        y_axis_title='Niveles de agua',
        y_axis_units='m',
        series=[
            {'name': 'Historico','data': data},
            {'name': 'Nivel Minimo de Operacion', 'data': min_level, 'type': 'line', 'color': '#660066'},
            {'name': 'Nivel Maximo de Operacion', 'data': max_level, 'type': 'line', 'color': '#FF0000'}
            ],
        y_min = site_config['ymin']
    )


    outflow_edit = TableView(column_names=('Dia', 'Caudal de Salida (cms)', 'Tiempo de salida (horas)'),
                             rows=[(forecasteddata[0], '0', '0'),
                                   (forecasteddata[1], '0', '0'),
                                   (forecasteddata[2], '0', '0'),
                                   (forecasteddata[3], '0', '0'),
                                   (forecasteddata[4], '0', '0'),
                                   (forecasteddata[5], '0', '0'),
                                   (forecasteddata[6], '0', '0'),
                                   ],
                             hover=True,
                             striped=True,
                             bordered=True,
                             condensed=True,
                             editable_columns=(False, 'Outflow', 'Time'),
                             row_ids=['day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7'],
                             classes="outflowtable"
                             )

    calculate = Button(display_text='Calcular Niveles del Embalse',
                       name='calculate',
                       style='',
                       icon='',
                       href='',
                       submit=False,
                       disabled=False,
                       attributes={"onclick": "calculatelevels()"},
                       classes='calcbut'
                       )

    outflow_button = Button(display_text='Ingresar caudales de salida',
                            name='dimensions',
                            style='',
                            icon='',
                            href='',
                            submit=False,
                            disabled=False,
                            attributes={"onclick": "outflowmodal()"},
                            classes='outflow_button'
                            )
    context = {
    	'site_urls':gen_urls(request),
    	'name':site_name,
        'timeseries_plot': timeseries_plot,
        'outflow_button': edit_passthrough(request,outflow_button),
        'calculate': calculate,
        'outflow_edit': outflow_edit,
        'show_edit':has_permission(request, 'update_data')
    }

    return render(request, 'reservoir_management/site_renderer.html', context)

@login_required()
def reportar(request):
    """
    Controller for the app home page.
    """

    #these are the different inputs on the reportar page of the app
    dam_input = SelectInput(display_text='Seleccionar una presa',
                               name='dam',
                               multiple=False,
                               original=True,
                               options=[('Sabana Yegua', 'Sabana Yegua'),
                                        ('Sabaneta', 'Sabaneta'),
                                        ('Hatillo', 'Hatillo'),
                                        ('Tavera-Bao', 'Tavera-Bao'),
                                        ('Moncion', 'Moncion'),
                                        ('Rincon', 'Rincon'),
                                        ('Jiguey', 'Jiguey'),
                                        ('Valdesia', 'Valdesia'),
                                        ('Rio Blanco', 'Rio Blanco'),
                                        ('Pinalito', 'Pinalito'),
                                        ('Maguaca', 'Maguaca'),
                                        ('Chacuey', 'Chacuey')
                                        ],
                               attributes={"onchange": "get_min_max_operating_levels()"},
                            )

    level_input = TextInput(display_text='Nivel de Agua',
                           name='levelinput',
                           placeholder='Niveles de Operacion: Min-358 Max-396.4',
                           )


    today = datetime.datetime.now()
    year = str(today.year)
    month = str(today.strftime("%B"))
    day = str(today.day)
    date = month + ' ' + day + ', ' + year

    date_input = DatePicker(name='dateinput',
                             display_text='Dia',
                             autoclose=True,
                             format='MM d, yyyy',
                             start_date='2/15/2014',
                             start_view='month',
                             today_button=True,
                             initial= date)

    data = getrecentdata()
    table_view = TableView(column_names=('Tiempo','Tavera-Bao','Moncion','Rincon','Hatillo',
                                         'Jiguey','Valdesia','S. Yegua','Sabaneta','Rio Blanco',
                                         'Pinalito','Maguaca','Chacuey'),
                           rows=data,
                           hover=True,
                           striped=True,
                           bordered=True,
                           condensed=True)

    message_box = MessageBox(name='sampleModal',
                             title='Resumen de Entradas',
                             message='',
                             dismiss_button='Regresar',
                             affirmative_button='Proceder',
                             width=400,
                             affirmative_attributes='onclick=append();',
                             )

    download_button = Button(display_text='Descargar Datos',
                            name='download',
                            style='',
                            icon='',
                            href='file:///C:/Users/student/tethysdev/tethysapp-reservoir_management/tethysapp/reservoir_management/workspaces/app_workspace/DamLevel_DR_BYU 2018.xlsx',
                            submit=False,
                            disabled=False,
                            attributes={"onclick": "outflowmodal()"},
                            classes='outflow_button'
                            )


    context = {
        'site_urls':gen_urls(request),
        'dam_input': dam_input,
        'level_input':level_input,
        'date_input': date_input,
        'table_view': table_view,
        'message_box': message_box,
        'download_button': download_button,
        'show_edit':has_permission(request, 'update_data')

    }

    return render(request, 'reservoir_management/reportar.html', context)

def get_forecast_curve(request):
    get_data = request.GET

    try:
        levels = get_data['forecastlevels'].split(",")
        forecastdates = get_data['forecastdates'].split(",")
        res = get_data['res']

        datetimedates = []
        forecastlevel = []
        observeddates = []
        observedlevels = []

        for x in range(0,len(forecastdates)):
            datetimedates.append(datetime.datetime.strptime(forecastdates[x], "%Y-%m-%d"))
            forecastlevel.append(float(levels[x]))

        if res == 'Sabana_Yegua':
            res = 'S. Yegua'
        app_workspace = app.get_app_workspace()
        damsheet = os.path.join(app_workspace.path, 'DamLevel_DR_BYU 2018.xlsx')

        dfnan = pd.read_excel(damsheet)
        df1 = dfnan[['Nivel', res]]
        df = df1.dropna()[::-1]
        reslevels = (df[:15])

        for index, row in reslevels.iterrows():
            observeddates.append(datetime.datetime.strptime(str(row['Nivel'])[:10], "%Y-%m-%d"))
            observedlevels.append(row[res])

        forecast = go.Scatter(
            x=datetimedates,
            y=forecastlevel,
            fill='tozeroy',
            name='pronosticos'
        )

        observed = go.Scatter(
            x=observeddates,
            y=observedlevels,
            fill='tozeroy',
            name='observados'
        )

        layout = go.Layout(title="Niveles Observados y Pronosticados",
                           xaxis=dict(
                               title='Dia',
                               type='datetime'),
                           yaxis=dict(
                               title='Nivel del Emblase',
                               range=[float(min(min(forecastlevel),min(observedlevels)))-2.0, float(max(max(forecastlevel),max(observedlevels))) + 2.0]),
                           showlegend=True)

        chart_obj = PlotlyView(
            go.Figure(data=[forecast,observed],
                      layout=layout)
        )

        context = {
            'gizmo_object': chart_obj,
        }

        return render(request,'reservoir_management/gizmo_ajax.html', context)

    except Exception as e:
        print str(e)
        return JsonResponse({'error':'Unknown Error'})
