from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from decouple import config
import dash
from vTweet.dash_layout import define_layout
import dash_bootstrap_components as dbc
import tweepy

# Init main Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vtweet:vtweet!#%@localhost/vtweet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Init dash's app
dash_external_stylesheets = [dbc.themes.FLATLY]
dash_frontend = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/dash_frontend/',
    external_stylesheets=dash_external_stylesheets
)
define_layout(dash_frontend)

auth = tweepy.OAuthHandler(
    config('CONSUMER_KEY'), config('CONSUMER_SECRET'))
api = tweepy.API(auth)

# Create all models - CANNOT RECREATE AS PROCEDURES/FUNCTIONS ARE NOW DEPENDENT ON TABLES
# from vTweet.models import Database
# database = Database()

from vTweet import routes
