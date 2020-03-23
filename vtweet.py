import tweepy
from decouple import config
# from app import db
# from database import Hashtag


def get_tweets(query):
    auth = tweepy.OAuthHandler(
        config('CONSUMER_KEY'), config('CONSUMER_SECRET'))
    api = tweepy.API(auth)
    for tweet in tweepy.Cursor(api.search, q=query).items(1):
        return tweet
        # json_dict = tweet._json
        # hashtags = json_dict['hashtags']
        # print(hashtags)
        # return json_dict
        # hashtag = Hashtag(hashtag=)
        # for key in json_dict.keys():
        #     print(key, ":", json_dict[str(key)])
