# coding: utf8
import dash
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash_table.Format import Format, Group, Scheme, Symbol
import dash_table.FormatTemplate as FormatTemplate

import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import numpy as np
import pandas as pd

from plotly import graph_objects as go
import plotly.express as px

from flask_caching import Cache

from dateutil.relativedelta import relativedelta
from get_data import get_main_table, get_data_table, get_data_funnel, get_utm_medium_options, get_funnel, get_utm_capmaign_options
from flask import session, copy_current_request_context
from auth import authenticate_user, validate_login_session
from server import app, server

def get_time():
    return dt.now().date()
    # if now.hour < 16:
    #     return (dt.now() - relativedelta(days=+2)).date()
    # else:
    #     return (dt.now() - relativedelta(days=+1)).date()

def get_utms():
    utm = ['###']
    options = [{'label': i, 'value': i} for i in utm]
    return options

@validate_login_session
def create_layout(app):
    return html.Div([
        dcc.Location(id='home-url',pathname='/home'),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(            
                                    html.Img(
                                        src=app.get_asset_url("otlnal_logo.png"),
                                        className="logo",
                                    )
                                )
                            ], 
                            className = 'row'
                        ),
                        html.H1(
                            children='Дашборд регистрации онлайн-направления "Отличных Наличных"',
                            className="ten columns main-title",style={'margin-bottom': 10}),
                        html.Div([html.Button('Выйти',id='logout-button',n_clicks=0)]),
                        html.Hr()
                    ],  
                    className="row",
                )
            ],
            className="twelve columns offset-by-one",style={
            'margin-bottom': 0
        }),
        html.Div([
            html.H5(children='Отчет по воронке регистрации',style={
            'margin-bottom': 20
        }),
            html.H6(children='Дата отчета:',
                    className= "two columns"
                    ), 
            html.Div([
                dcc.DatePickerRange(
                    id='my-date-picker-range-1',
                    min_date_allowed=dt(2021, 1, 1),
                    max_date_allowed=get_time(),
                    initial_visible_month=dt(2021, 11, 1),
                    start_date=(dt.now() - relativedelta(days=+5)).date(),
                    end_date=get_time(),
                    display_format='DD.MM.YYYY',
                    style={'border': '0px'}
                    )], className = "six columns",  style={
                        'margin-bottom': 15
                        },
                    ),
            html.Div([
                html.Label('Форма регистрации:'),
                dcc.Dropdown(
                    id='type-1',
                    options=[
                            {'label': 'F_VUE', 'value': 'f'},
                            {'label': 'G_VUE', 'value': 'g'},
                            {'label': 'H_VUE', 'value': 'h'},
                            {'label': 'K_VUE', 'value': 'k'},
                            {'label': 'L_VUE', 'value': 'l'},
                            ],
                            value='f',
                            clearable=False
                            )], className = "six columns",
                            style={
                                'margin-bottom': 5, 'display': 'block'
                                }
                    ),
                ],  className="six columns offset-by-one",
                style={
                    'margin-bottom': 10
                    }
                    ),
        html.Div(
            [html.Div([
                    dcc.Graph(id='FunnelDashboard-1'
                            )
                ],    className="eleven columns", style={
            'margin-bottom': 0
            }),
            html.Div([
                    dcc.RadioItems(
                            id = 'radio-button',
                            options=[
                                {'label': 'Суммарно за выбранный период', 'value': 'sum'},
                                {'label': 'По дням', 'value': 'by_days'},
                                {'label': 'По месяцам', 'value': 'by_months'}
                            ],
                            value='sum'
                        )], className = "eleven columns",  style={
                        'margin-bottom': 5,
                        'margin-left': 5
                        }), 
                html.Div([
                    dash_table.DataTable(
                        id='my-datatable-1',
                        page_size=1000,
                        export_format="xlsx",
                        style_cell={'fontSize':14, 'font-family':'sans-serif','height': '100%','whiteSpace': 'normal','padding': '5px'},
                        style_table={'overflowX': 'auto'},
                        style_as_list_view=False,
                        style_header={'fontWeight': 'bold'},
                )],    className="eleven columns", style={
            'margin-bottom': 0
            }),
            html.Div([
                html.Hr(),
                html.H5(children='KPI по сайту и мобильному приложению'),
                    dash_table.DataTable(
                        id='my-datatable-2',
                        page_size=1000,
                        export_format="xlsx",
                        style_cell={'fontSize':11, 'font-family':'sans-serif','height': '100%','whiteSpace': 'normal','padding': '5px'},
                        style_table={'overflowX': 'auto'},
                        merge_duplicate_headers = True,
                        style_as_list_view=False,
                        style_header={'fontWeight': 'bold'}
                                ),
                html.Hr()
                ],    className="eleven columns", style={'margin-bottom': 0
                }),
            html.Div([
                html.H5(children='Ежедневный персональный отчет по партнерам')]
                                ,className= "ten columns", style={
            'margin-bottom': 10
                                }),
            html.Div([
                dcc.DatePickerRange(
                                    id='my-date-picker-range-2',
                                    min_date_allowed=dt(2021, 11, 1),
                                    max_date_allowed=get_time(),
                                    initial_visible_month=dt(2021, 11, 1),
                                    start_date=(dt.now() - relativedelta(days=+7)).date(),
                                    end_date=get_time(),
                                    display_format='DD.MM.YYYY',
                                    style={
                                        'border': '0px'
                                    }
                            ),
                html.Label('Тип клиента:'),
                    dcc.Dropdown(
                            id='dropdown_type_client',
                            options=[
                                {'label': 'Новые', 'value': 'new'},
                                {'label': 'Повторные', 'value': 'again'}
                            ],
                            value=['new', 'again'],
                            multi=True
                        ),
                    html.Label('utm_source:'),
                    dcc.Dropdown(
                            id='dropdown_utm_source',
                            options=get_utms(),
                            value=[],
                            multi=True
                        ),
                    html.Label('utm_medium:'),
                    dcc.Dropdown(id='dropdown_utm_medium',
                                multi=True),
                    html.Label('utm_capmaign:'),
                    dcc.Dropdown(id='dropdown_utm_campaign',
                                multi=True),
                            ], className = "four columns",  style={
                        'margin-bottom': 15
                    }),   
            html.Div([
                    dash_table.DataTable(
                        id='my-datatable-3',
                        page_size=1000,
                        export_format="xlsx",
                        style_cell={'fontSize':14, 'font-family':'sans-serif','height': '100%','whiteSpace': 'normal','padding': '5px'},
                        style_table={'overflowX': 'auto'},
                        style_as_list_view=False,
                        style_header={'fontWeight': 'bold'},
                        tooltip_duration=None,
                )],    className="eleven columns", style={
            'margin-bottom': 50
            }),
            ], className = "twelve columns offset-by-one",  style={
                            'margin-bottom': 100
        }),
    ],  className='ten columns offset-by-two ')

def login_layout():
    return html.Div(
        [
            dcc.Location(id='home-url',pathname='/login',refresh=False),
            dbc.Container(
                [
                    dbc.Row(
                        dbc.Col(
                            dbc.Card(
                                [
                                    html.H4('Авторизация',className='card-title'),
                                    dcc.Input(id='login-email',placeholder='Логин'),
                                    dcc.Input(id='login-password',placeholder='Пароль',type='password'),
                                    html.Button('Войти',id='login-button'),
                                    html.Br(),
                                    html.Div(id='login-alert')
                                ],
                                body=True
                            ),
                            width=6
                        ),
                        justify='center'
                    )
                ]
            )
        ]
    )


app.layout = html.Div(
    [
        dcc.Location(id='url',refresh=False),
        html.Div(
            #login_layout(),
            id='page-content'
        ),
    ]
)


@app.callback(
    dash.dependencies.Output('page-content','children'),
    [dash.dependencies.Input('url','pathname')]
)
def router(url):
    if url=='/home':
        return create_layout(app)
    elif url == "/otlnal-month-report/exit":
        return login_layout()
    else:
        return login_layout()

# authenticate 
@app.callback(
    [dash.dependencies.Output('url','pathname'),
     dash.dependencies.Output('login-alert','children')],
    [dash.dependencies.Input('login-button','n_clicks')],
    [dash.dependencies.State('login-email','value'),
     dash.dependencies.State('login-password','value')])
def login_auth(n_clicks,email,pw):
    '''
    check credentials
    if correct, authenticate the session
    otherwise, authenticate the session and send user to login
    '''
    if n_clicks is None or n_clicks==0:
        return no_update,no_update
    credentials = {'user':email,"password":pw}
    if authenticate_user(credentials):
        session['authed'] = True
        return '/home',''
    session['authed'] = False
    return no_update,dbc.Alert('Ошибка входа! Проверьте введенные данные',color='danger',dismissable=True)

@app.callback(
    dash.dependencies.Output('home-url','pathname'),
    [dash.dependencies.Input('logout-button','n_clicks')]
)
def logout_(n_clicks):
    '''clear the session and send user to login'''
    if n_clicks is None or n_clicks==0:
        return no_update
    session['authed'] = False
    return '/login'

@app.callback([dash.dependencies.Output('my-datatable-1', 'data'),
               dash.dependencies.Output('my-datatable-1', 'columns')], 
              [dash.dependencies.Input('radio-button', 'value'),
                dash.dependencies.Input('my-date-picker-range-1', 'start_date'),
                dash.dependencies.Input('my-date-picker-range-1', 'end_date'),
                dash.dependencies.Input('type-1', 'value')])
def update_table_1(display ,start_date, end_date, type):
    data = get_main_table(display ,type, dt.strptime(start_date, '%Y-%m-%d').date(), dt.strptime(end_date, '%Y-%m-%d').date())
    return data.to_dict('records'), [{"name": i, "id": i, 'type': 'numeric',
            'format': Format(
                scheme=Scheme.fixed, 
                precision=1,
                group=Group.yes,
                groups=3,
                group_delimiter=' ',
                decimal_delimiter=',')} for i in data.columns]

@app.callback([dash.dependencies.Output('my-datatable-2', 'data'),
               dash.dependencies.Output('my-datatable-2', 'columns')], 
              [dash.dependencies.Input('my-date-picker-range-1', 'start_date'),
                dash.dependencies.Input('my-date-picker-range-1', 'end_date')])
def update_table_2(start_date, end_date):
    data = get_data_table()
    n_col = {"Месяц":" ","Всего посетителей без PersonID + начатые регистрации":"Конверсия из посетителя в начало регистрации","Количество начатых регистраций":"Конверсия из посетителя в начало регистрации","Конверсия":"Конверсия из посетителя в начало регистрации","Количество начатых регистраций.":"Конверсия из начала в завершение регистрации","Количество успешных регистраций":"Конверсия из начала в завершение регистрации","Конверсия.":"Конверсия из начала в завершение регистрации","Количество сессий":"Конверсия визита повторного клиента в выдачу","Количество займов":"Конверсия визита повторного клиента в выдачу",".Конверсия":"Конверсия визита повторного клиента в выдачу"}
    col = [{"name": [n_col[i], i], "id": i, 'type': 'numeric', 'format': Format(
                scheme=Scheme.fixed, 
                precision=1,
                group=Group.yes,
                groups=3,
                group_delimiter=' ',
                decimal_delimiter=',')} for i in n_col]
    return data.to_dict('records'), col

@app.callback(
    dash.dependencies.Output('FunnelDashboard-1', 'figure'),
    [dash.dependencies.Input('my-date-picker-range-1', 'start_date'),
    dash.dependencies.Input('my-date-picker-range-1', 'end_date'),
    dash.dependencies.Input('type-1', 'value')])
def update_funnel_1(start_date, end_date, type):
    y_val, x_val, color_val = get_data_funnel(type ,dt.strptime(start_date, '%Y-%m-%d').date(), dt.strptime(end_date, '%Y-%m-%d').date())
    return {
        'data':[go.Funnel(
                    y = y_val,
                    x = x_val,
                    marker = {"color": color_val })],
        'layout': {
            'height': 600,
            'margin': {
                'l': 250
            }
        }
    }

@app.callback(
    dash.dependencies.Output('dropdown_utm_medium', 'options'),
    [dash.dependencies.Input('dropdown_utm_source', 'value'),
    dash.dependencies.Input('my-date-picker-range-1', 'start_date'),
    dash.dependencies.Input('my-date-picker-range-1', 'end_date')])
def set_cities_options(selected_utm_source, start_date, end_date):
    all_options = get_utm_medium_options(selected_utm_source, dt.strptime(start_date, '%Y-%m-%d').date(), dt.strptime(end_date, '%Y-%m-%d').date())
    return all_options

@app.callback(
    dash.dependencies.Output('dropdown_utm_medium', 'value'),
    dash.dependencies.Input('dropdown_utm_medium', 'options'))
def set_cities_value(available_options):
    return []

@app.callback(
    dash.dependencies.Output('dropdown_utm_campaign', 'options'),
    [dash.dependencies.Input('dropdown_utm_source', 'value'),
    dash.dependencies.Input('dropdown_utm_medium', 'value'),
    dash.dependencies.Input('my-date-picker-range-1', 'start_date'),
    dash.dependencies.Input('my-date-picker-range-1', 'end_date')])
def set_cities_options(selected_utm_source, selected_utm_medium,start_date, end_date):
    all_options = get_utm_capmaign_options(selected_utm_source, selected_utm_medium,dt.strptime(start_date, '%Y-%m-%d').date(), dt.strptime(end_date, '%Y-%m-%d').date())
    return all_options

@app.callback(
    dash.dependencies.Output('dropdown_utm_campaign', 'value'),
    dash.dependencies.Input('dropdown_utm_campaign', 'options'))
def set_cities_value(available_options):
    return []

@app.callback([dash.dependencies.Output('my-datatable-3', 'data'),
               dash.dependencies.Output('my-datatable-3', 'columns'),
               dash.dependencies.Output('my-datatable-3', 'tooltip_data')], 
              [dash.dependencies.Input('my-date-picker-range-2', 'start_date'),
                dash.dependencies.Input('my-date-picker-range-2', 'end_date'),
                dash.dependencies.Input('dropdown_type_client', 'value'),
                dash.dependencies.Input('dropdown_utm_source', 'value'),
                dash.dependencies.Input('dropdown_utm_medium', 'value'),
                dash.dependencies.Input('dropdown_utm_campaign', 'value')
                ])
def update_table_3(start_date, end_date, type, utm_source, utm_medium, utm_campaign):
    data = get_funnel(dt.strptime(start_date, '%Y-%m-%d').date(), dt.strptime(end_date, '%Y-%m-%d').date(), type, utm_source, utm_medium, utm_campaign)
    description = {
        '1': 'Посещений otlnal.ru',
        '2': 'Формула = (Интерес / Сессии) * 100%',
        '3': 'Пользователи, которые нажали на кнопку «Получить деньги»',
        '4': 'Формула = (Интерес / Старт) * 100%',
        '5': 'Пользователи, которые нажали «Зарегистрироваться»',
        '6': 'Формула = (Контакты / Старт) * 100%',
        '7': 'Пользователи, которые начали регистрацию и заполнили шаг с контактами personrequestID',
        '8': 'Формула = (завершенные регистрации / контакты) * 100%',
        '9': 'Пользователи, которые заполнили форму и по ним создан personID',
        '10': 'Формула = (одобрения / завершенные регистрации) * 100%',
        '11': 'Клиенты, которые получили положительное решение о выдаче займа',
        '12': 'Формула = (идентификация / одобрения) * 100%',
        '13': 'Клиенты, которые успешно загрузили фото, и мы это приняли',
        '14': 'Формула = (первая выдача / идентификация) * 100%',
        '15': 'Клиенты, которые успешно получили займы',
        '16': 'Сумма выдач',
        '17': 'Средний чек',
        '18': 'Формула = (первая выдача / сессии) * 100%'
        }
    tooltip_data=[{
                col: description[str(i)] for col in data.columns} for i in range(1,len(data)+1)]

    return data.to_dict('records'), [{"name": i, "id": i, 'type': 'numeric',
            'format': Format(
                scheme=Scheme.fixed, 
                precision=2,
                group=Group.yes,
                groups=3,
                group_delimiter=' ',
                decimal_delimiter=',')} for i in data.columns], tooltip_data

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=5009, debug=True, use_reloader=False)
