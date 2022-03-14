import dash
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    #external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.config.suppress_callback_exceptions = True
app.title = 'Дашборд регистрации'

server = app.server
server.config['SECRET_KEY'] = '###'
