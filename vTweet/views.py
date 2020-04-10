import tweepy
import logging
from decouple import config
from vTweet.models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError as sqlIntegrityError
from sqlalchemy.orm.exc import FlushError as sqlPKError
from vTweet import db, api
from datetime import datetime
from geopy.geocoders import Nominatim
import csv


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logfile_handler = logging.FileHandler('vTweet/insertion.log', mode='w')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(message)s', datefmt='%H:%M:%S')
logfile_handler.setFormatter(formatter)
logger.addHandler(logfile_handler)


def fetch_tweet_ids(filename='corona_tweets_21.csv'):
    with open(filename) as f:
        reader = csv.reader(f)
        tweet_ids = [row[0] for row in reader]
    return tweet_ids


def insert_tweets_from_object(tweet):
    json_dict = tweet._json

    # Temporarily disable
    logging.disable(logging.CRITICAL)

    # Hashtags
    logger.info("HASHTAGS")
    count, hashtag_models = insert_hashtags(json_dict)
    logger.info('%d HASHTAGS COMMITTED', count)

    # Coordinates
    # logger.info('COORDINATES')
    # insert_coordinates(json_dict)
    # logger.info('COORDINATES COMMITTED')

    # Place
    logger.info('PLACE')
    place_id = insert_place(json_dict)
    logger.info('PLACE COMMITTED')

    # Tweets
    logger.info('TWEET')
    insert_tweet(json_dict, place_id)
    logger.info('TWEET ADDED')

    # Tweeted User
    logger.info('OPs OF TWEET')
    insert_user(json_dict)
    logger.info('OPs OF TWEET ADDED')

    # Retweeted User
    logger.info('RETWEETED USER')
    insert_retweeted_user(json_dict)
    logger.info('RETWEETED USER ADDED')

    # Mentioned Users
    logger.info('MENTIONED USER')
    insert_mentioned_user(json_dict)
    logger.info('MENTIONED USER ADDED')

    # print(tweet)
    logger.info('TWEET_HASHTAGS')
    insert_tweet_hashtags(json_dict, hashtag_models)
    logger.info('TWEET_HASHTAGS ADDED')

    logger.info('\n\n')


def insert_tweets_data(query):

    # May not work for Gujarati cities.
    # Not enough people posting with location info.
    # NYC
    LAT = 40.712776
    LONG = -74.005974

    geocode = str(LAT) + ',' + str(LONG) + ',1000mi'
    for i, tweet in enumerate(tweepy.Cursor(api.search, q=query).items(10)):
        logger.info('TWEET NO. %d', i)
        json_dict = tweet._json

        # Hashtags
        logger.info("HASHTAGS")
        count, hashtag_models = insert_hashtags(json_dict)
        logger.info('%d HASHTAGS COMMITTED', count)

        # # Coordinates
        # logger.info('COORDINATES')
        # insert_coordinates(json_dict)
        # logger.info('COORDINATES COMMITTED')

        # Place
        logger.info('PLACE')
        place_id = insert_place(json_dict)
        logger.info('PLACE COMMITTED')

        # Tweets
        logger.info('TWEET')
        insert_tweet(json_dict, place_id)
        logger.info('TWEET ADDED')

        # Tweeted User
        logger.info('OPs OF TWEET')
        insert_user(json_dict)
        logger.info('OPs OF TWEET ADDED')

        # Retweeted User
        logger.info('RETWEETED USER')
        insert_retweeted_user(json_dict)
        logger.info('RETWEETED USER ADDED')

        # Mentioned Users
        logger.info('MENTIONED USER')
        insert_mentioned_user(json_dict)
        logger.info('MENTIONED USER ADDED')

        # print(tweet)
        logger.info('TWEET_HASHTAGS')
        insert_tweet_hashtags(json_dict, hashtag_models)
        logger.info('TWEET_HASHTAGS ADDED')

        logger.info('\n\n')


def insert_hashtags(json_dict):
    hashtags = json_dict['entities']['hashtags']
    hashtag_models = [Hashtag(hashtag=hashtags[i]['text'])
                      for i in range(len(hashtags))]

    for tag in hashtag_models:
        logger.info(tag.hashtag)
        db.session.add(tag)
        # TODO: Replace this exception handling mechanism by an SQL trigger
        try:
            db.session.commit()
        except (sqlIntegrityError, sqlPKError):
            db.session.rollback()
            pass

    return len(hashtag_models), hashtag_models


def insert_place(json_dict):
    place_id = None
    place = None
    geolocator = Nominatim(user_agent="vtweet", timeout=20)
    try:
        place_id = json_dict['place']['id']
        name = json_dict['place']['name']
        country = json_dict['place']['country']
        country_code = json_dict['place']['country_code']
        location = geolocator.geocode(country)
        latitude = location.latitude
        longitude = location.longitude
        place = Place(place_id=place_id, name=name,
                      latitude=latitude, longitude=longitude, country_code=country_code)
        country = Country(country_code=country_code, country=country)
        logger.info(place.name)
        # try:
        #     coordinates = json_dict['coordinates']
        #     logger.info('Coordinates:', coordinates)
        #     logger.info(type(coordinates))
        # except KeyError:
        #     pass
        db.session.add(place)
        db.session.add(country)
    except TypeError:
        pass
    try:
        db.session.commit()
    except (sqlIntegrityError, sqlPKError):
        db.session.rollback()
        pass

    return place_id


# def insert_coordinates(json_dict):
#     geolocator = Nominatim(user_agent="vtweet", timeout=20)
#     try:
#         country = json_dict['place']['country']
#         country_code = json_dict['place']['country_code']
#         location = geolocator.geocode(country)
#         coordinates = Coordinates(
#             country_code=country_code, latitude=location.latitude, longitude=location.longitude)
#         db.session.add(coordinates)
#     except TypeError:
#         return
#     try:
#         db.session.commit()
#     except (sqlIntegrityError, sqlPKError):
#         db.session.rollback()


def insert_tweet(json_dict, place_id):
    created_at = json_dict['created_at']
    # Hoping that the numbers are zero padded
    created_at = datetime.strptime(
        created_at, '%a %b %d %H:%M:%S +0000 %Y')
    try:
        possibly_sensitive = json_dict['possibly_sensitive']
    except KeyError:
        possibly_sensitive = False
    tweet = BaseTweet(tweet_id=json_dict['id'], tweet_id_str=json_dict['id_str'], tweet_text=json_dict['text'], source=json_dict['source'], favorited=json_dict[
        'favorited'], retweeted=json_dict['retweeted'], favorite_count=json_dict['favorite_count'], retweet_count=json_dict['retweet_count'], result_type=None, created_at=created_at, lang=json_dict['lang'], possibly_sensitive=possibly_sensitive, place_id=place_id)
    db.session.add(tweet)
    try:
        db.session.commit()
        logger.info(tweet.tweet_id)
    except (sqlIntegrityError, sqlPKError):
        db.session.rollback()
        pass


def insert_user(json_dict):
    user_json = json_dict['user']
    id = user_json['id']
    id_str = user_json['id_str']
    name = user_json['name']
    screen_name = user_json['screen_name']
    followers_count = user_json['followers_count']
    verified = user_json['verified']
    profile_image_url_https = user_json['profile_image_url_https']
    favourites_count = user_json['favourites_count']

    user = User(id=id, id_str=id_str, name=name, screen_name=screen_name, followers_count=followers_count,
                verified=verified, profile_image_url_https=profile_image_url_https, favourites_count=favourites_count)
    db.session.add(user)
    try:
        db.session.commit()
        logger.info(user.id)
    except (sqlIntegrityError, sqlPKError):
        db.session.rollback()
        pass

    logger.info('TWEET USER')
    tweet_user = TweetUser(user_id=id, tweet_id=json_dict['id'])
    db.session.add(tweet_user)
    try:
        db.session.commit()
        logger.info(tweet_user.user_id)
    except (sqlIntegrityError, sqlPKError):
        db.session.rollback()
        pass
    logger.info('TWEET USER ADDED')


def insert_retweeted_user(json_dict):
    try:
        retweeted_dict = json_dict['retweeted_status']
        user_json = retweeted_dict['user']
        id = user_json['id']
        id_str = user_json['id_str']
        name = user_json['name']
        screen_name = user_json['screen_name']
        followers_count = user_json['followers_count']
        verified = user_json['verified']
        profile_image_url_https = user_json['profile_image_url_https']
        favourites_count = user_json['favourites_count']

        user = User(id=id, id_str=id_str, name=name, screen_name=screen_name, followers_count=followers_count,
                    verified=verified, profile_image_url_https=profile_image_url_https, favourites_count=favourites_count)
        db.session.add(user)
        try:
            db.session.commit()
        except (sqlIntegrityError, sqlPKError):
            db.session.rollback()
            pass

        retweeted_user = RetweetedUser(
            user_id=id, tweet_id=json_dict['id'])
        logger.info(retweeted_user.user_id)
        db.session.add(retweeted_user)
        try:
            db.session.commit()
        except (sqlIntegrityError, sqlPKError):
            db.session.rollback()
            pass
    except KeyError:
        pass


def insert_mentioned_user(json_dict):
    user_mentions = json_dict['entities']['user_mentions']
    for user_mentioned in user_mentions:
        id = user_mentioned['id']

        # Lot of people mention their own account
        if (id == json_dict['user']['id']):
            continue

        # And a retweet always counts as a mention
        try:
            if (id == json_dict['retweeted_status']['user']['id']):
                continue
        except KeyError:
            pass

        try:
            user_obj = api.get_user(id=id)
        except tweepy.error.TweepError:
            continue
        user = User(id=id, id_str=user_obj.id_str, name=user_obj.name, screen_name=user_obj.screen_name, followers_count=user_obj.followers_count,
                    verified=user_obj.verified, profile_image_url_https=user_obj.profile_image_url_https, favourites_count=user_obj.favourites_count)
        logger.info(user.id)
        db.session.add(user)
        try:
            db.session.commit()
        except (sqlIntegrityError, sqlPKError):
            db.session.rollback()
            pass


def insert_tweet_hashtags(json_dict, hashtag_models):
    for tag in hashtag_models:
        tweet_hashtag = TweetHashtag(
            tweet_id=json_dict['id'], hashtag=tag.hashtag)
        db.session.add(tweet_hashtag)
        logger.info(tweet_hashtag.tweet_id)
        try:
            db.session.commit()
        except (sqlIntegrityError, sqlPKError):
            db.session.rollback()
            pass
