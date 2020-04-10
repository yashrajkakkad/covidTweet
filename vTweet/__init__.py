from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from decouple import config
import dash
import tweepy

# Init main Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vtweet:vtweet!#%@localhost/vtweet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

auth = tweepy.OAuthHandler(
    config('CONSUMER_KEY'), config('CONSUMER_SECRET'))
api = tweepy.API(auth)

# Create all models - CANNOT RECREATE AS PROCEDURES/FUNCTIONS ARE NOW DEPENDENT ON TABLES
from vTweet.models import Database
database = Database()

from vTweet import routes
