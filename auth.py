from functools import wraps
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import session
import ldap 


def authenticate_user(credentials):
    auth = False
    LDAP_SERVER = '###'
    BASE_DN = '###'  
    LDAP_LOGIN = credentials['user']
    LDAP_PASSWORD = credentials['password']
    OBJECT_TO_SEARCH = f"""###"""
    ATTRIBUTES_TO_SEARCH = ['memberOf']
    try:
        connect = ldap.initialize(LDAP_SERVER)
        connect.set_option(ldap.OPT_REFERRALS, 0) 
        connect.simple_bind_s(LDAP_LOGIN, LDAP_PASSWORD)
        result = connect.search_s(BASE_DN, ldap.SCOPE_SUBTREE, OBJECT_TO_SEARCH, ATTRIBUTES_TO_SEARCH)
        for i in result[0][1]['memberOf']:
            if '###' in i.decode('utf-8'):
                auth = True
    except TypeError:
        auth = False
    except ldap.INVALID_CREDENTIALS:
        auth = False
    except ldap.OPERATIONS_ERROR:
        auth = False
    return auth

def validate_login_session(f):
    '''
    takes a layout function that returns layout objects
    checks if the user is logged in or not through the session. 
    If not, returns an error with link to the login page
    '''
    @wraps(f)
    def wrapper(*args,**kwargs):
        if session.get('authed',None)==True:
            return f(*args,**kwargs)
        return html.Div(
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H3('Ошибка авторизации',className='card-title'),
                                html.A(dcc.Link('Войти',href='/login'))
                            ],
                            body=True
                        )
                    ],
                    width=5
                ),
                justify='center'
            )
        )
    return wrapper
