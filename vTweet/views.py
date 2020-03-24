import tweepy
from decouple import config
from vTweet.models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError as sqlIntegrityError
from vTweet import db, api


def get_tweets(query):
    for tweet in tweepy.Cursor(api.search, q=query).items(50):
        json_dict = tweet._json
        # Hashtags
        hashtags = json_dict['entities']['hashtags']
        print(hashtags)
        print(type(hashtags))
        hashtag_models = [Hashtag(hashtag=hashtags[i]['text'])
                          for i in range(len(hashtags))]

        for tag in hashtag_models:
            print(tag.hashtag)
            db.session.add(tag)
            # TODO: Replace this exception handling mechanism by an SQL trigger
            try:
                db.session.commit()
            except sqlIntegrityError:
                db.session.rollback()
                pass

        # Place
        print('Place: ')
        try:
            place_id = json_dict['place']['id']
            name = json_dict['place']['name']
            country = json_dict['place']['country']
            country_code = json_dict['place']['country_code']
            print(name)
            place = Place(place_id=place_id, name=name,
                          country=country, country_code=country_code)
            db.session.add(place)
        except TypeError:
            pass
        try:
            db.session.commit()
        except sqlIntegrityError:
            db.session.rollback()
            pass
        print('Changes committed')
