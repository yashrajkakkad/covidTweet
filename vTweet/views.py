import tweepy
import logging
from decouple import config
from vTweet.models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError as sqlIntegrityError
from vTweet import db, api
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logfile_handler = logging.FileHandler('vTweet/insertion.log', mode='w')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(message)s', datefmt='%H:%M:%S')
logfile_handler.setFormatter(formatter)
logger.addHandler(logfile_handler)


def insert_tweets(query):
    BENG_LAT = 12.971599
    BENG_LONG = 77.594566

    # May not work for Gujarati cities. Not enough people posting with location info

    geocode = str(BENG_LAT) + ',' + str(BENG_LONG) + ',1mi'
    for tweet in tweepy.Cursor(api.search, q=query, geocode=geocode).items(10):
        json_dict = tweet._json

        # Hashtags
        hashtags = json_dict['entities']['hashtags']
        hashtag_models = [Hashtag(hashtag=hashtags[i]['text'])
                          for i in range(len(hashtags))]

        logger.info("HASHTAGS")
        for tag in hashtag_models:
            db.session.add(tag)
            # TODO: Replace this exception handling mechanism by an SQL trigger
            try:
                db.session.commit()
                logger.info(tag.hashtag)
            except sqlIntegrityError:
                db.session.rollback()
                pass
        logger.info('HASHTAGS COMMITTED')

        # Place
        logger.info('PLACES')
        place_id = None
        place = None
        try:
            place_id = json_dict['place']['id']
            name = json_dict['place']['name']
            country = json_dict['place']['country']
            country_code = json_dict['place']['country_code']
            place = Place(place_id=place_id, name=name,
                          country=country, country_code=country_code)
            db.session.add(place)
        except TypeError:
            pass
        try:
            db.session.commit()
            logger.info(place.name)
        except sqlIntegrityError:
            db.session.rollback()
            pass
        logger.info('PLACES COMMITTED')

        # Tweets
        logger.info('TWEETS')
        created_at = json_dict['created_at']
        # Hoping that the numbers are zero padded
        created_at = datetime.strptime(
            created_at, '%a %b %d %H:%M:%S +0000 %Y')
        try:
            possibly_sensitive = json_dict['possibly_sensitive']
        except KeyError:
            possibly_sensitive = False
        tweet = BaseTweet(tweet_id=json_dict['id'], tweet_id_str=json_dict['id_str'], source=json_dict['source'], favorited=json_dict[
            'favorited'], retweeted=json_dict['retweeted'], favorite_count=json_dict['favorite_count'], retweet_count=json_dict['retweet_count'], result_type=json_dict['metadata']['result_type'], created_at=created_at, lang=json_dict['lang'], possibly_sensitive=possibly_sensitive, place_id=place_id)
        db.session.add(tweet)
        try:
            db.session.commit()
            logger.info(tweet.tweet_id)
        except sqlIntegrityError:
            db.session.rollback()
            pass
        logger.info('TWEETS ADDED')

        # Tweeted User
        logger.info('OPs OF TWEETS')
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
        except sqlIntegrityError:
            db.session.rollback()
            pass
        logger.info('OPs OF TWEETS ADDED')

        logger.info('TWEET USERS')
        tweet_user = TweetUser(user_id=id, tweet_id=json_dict['id'])
        db.session.add(tweet_user)
        try:
            db.session.commit()
            logger.info(tweet_user.user_id)
        except sqlIntegrityError:
            db.session.rollback()
            pass
        logger.info('TWEET USERS ADDED')

        # Retweeted User
        logger.info('RETWEETED USERS')
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
            except sqlIntegrityError:
                db.session.rollback()
                pass

            retweeted_user = RetweetedUser(
                user_id=id, tweet_id=json_dict['id'])
            db.session.add(retweeted_user)
            try:
                db.session.commit()
                logger.info(retweeted_user.id)
            except sqlIntegrityError:
                db.session.rollback()
                pass
        except KeyError:
            pass
        logger.info('RETWEETED USERS ADDED')

        # Mentioned Users
        logger.info('MENTIONED USERS')
        user_mentions = json_dict['entities']['user_mentions']
        for user_mentioned in user_mentions:
            id = user_mentioned['id']
            try:
                user_obj = api.get_user(id=id)
            except tweepy.error.TweepError:
                continue
            user = User(id=id, id_str=user_obj.id_str, name=user_obj.name, screen_name=user_obj.screen_name, followers_count=user_obj.followers_count,
                        verified=user_obj.verified, profile_image_url_https=user_obj.profile_image_url_https, favourites_count=user_obj.favourites_count)
            db.session.add(user)
            try:
                db.session.commit()
            except sqlIntegrityError:
                db.session.rollback()
                pass
        logger.info('MENTIONED USERS ADDED')

        # print(tweet)
        logger.info('TWEET_HASHTAGS')
        for tag in hashtag_models:
            tweet_hashtag = TweetHashtag(
                tweet_id=json_dict['id'], hashtag=tag.hashtag)
            db.session.add(tweet_hashtag)
            try:
                db.session.commit()
                logger.info(tweet_hashtag.tweet_id)
            except sqlIntegrityError:
                db.session.rollback()
                pass
        logger.info('TWEET HASHTAGS ADDED')

        logger.info('\n\n')
