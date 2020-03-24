import tweepy
from decouple import config
from vTweet.models import *
from sqlalchemy.orm import sessionmaker
from vTweet import db


def get_tweets(query):
    auth = tweepy.OAuthHandler(
        config('CONSUMER_KEY'), config('CONSUMER_SECRET'))
    api = tweepy.API(auth)
    for tweet in tweepy.Cursor(api.search, q=query).items(1):
        json_dict = tweet._json
        hashtags = json_dict['entities']['hashtags']
        return hashtags
