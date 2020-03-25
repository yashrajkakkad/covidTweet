from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from decouple import config
import tweepy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vtweet:vtweet!#%@localhost/vtweet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

auth = tweepy.OAuthHandler(
    config('CONSUMER_KEY'), config('CONSUMER_SECRET'))
api = tweepy.API(auth)

# Create all models
from vTweet.models import Database
database = Database()

from vTweet import routes
