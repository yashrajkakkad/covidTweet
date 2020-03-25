import tweepy
from decouple import config
from vTweet.models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError as sqlIntegrityError
from vTweet import db, api
from datetime import datetime


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
        print('Hashtags commited')

        # Place
        print('Place: ')
        place_id = None
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
        print('Place committed')

        # Tweets
        created_at = json_dict['created_at']
        print(type(created_at))
        print(created_at)
        # Hoping that the numbers are zero padded
        created_at = datetime.strptime(
            created_at, '%a %b %d %H:%M:%S +0000 %Y')
        print(created_at)
        print(type(created_at))
        try:
            possibly_sensitive = json_dict['possibly_sensitive']
        except KeyError:
            possibly_sensitive = False
        tweet = BaseTweet(tweet_id=json_dict['id'], tweet_id_str=json_dict['id_str'], source=json_dict['source'], favorited=json_dict[
            'favorited'], retweeted=json_dict['retweeted'], favorite_count=json_dict['favorite_count'], retweet_count=json_dict['retweet_count'], result_type=json_dict['metadata']['result_type'], created_at=created_at, lang=json_dict['lang'], possibly_sensitive=possibly_sensitive, place_id=place_id)
        db.session.add(tweet)
        try:
            db.session.commit()
        except sqlIntegrityError:
            db.session.rollback()
            pass
        print('Tweet added')

        # Tweeted User
        print('Tweeted Users: ')
        user_json = json_dict['user']
        id = user_json['id']
        id_str = user_json['id_str']
        name = user_json['name']
        screen_name = user_json['screen_name']
        followers_count = user_json['followers_count']
        print(followers_count)
        print(type(followers_count))
        verified = user_json['verified']
        print(verified)
        print(type(verified))
        profile_image_url_https = user_json['profile_image_url_https']
        print(profile_image_url_https)
        print(type(profile_image_url_https))
        favourites_count = user_json['favourites_count']

        user = User(id=id, id_str=id_str, name=name, screen_name=screen_name, followers_count=followers_count,
                    verified=verified, profile_image_url_https=profile_image_url_https, favourites_count=favourites_count)
        db.session.add(user)
        try:
            db.session.commit()
            print('User added')
        except sqlIntegrityError:
            db.session.rollback()
            pass

        # tweet_user = TweetUser(user_id=id, tweet_id=json_dict['id'])
        # db.session.add(tweet_user)
        # try:
        #     db.session.commit()
        #     print('Tweet User added')
        # except sqlIntegrityError:
        #     db.session.rollback()
        #     pass

        # Retweeted User
        try:
            retweeted_dict = json_dict['retweeted_status']
            user_json = retweeted_dict['user']
            id = user_json['id']
            id_str = user_json['id_str']
            name = user_json['name']
            screen_name = user_json['screen_name']
            followers_count = user_json['followers_count']
            print(followers_count)
            print(type(followers_count))
            verified = user_json['verified']
            print(verified)
            print(type(verified))
            profile_image_url_https = user_json['profile_image_url_https']
            print(profile_image_url_https)
            print(type(profile_image_url_https))
            favourites_count = user_json['favourites_count']

            user = User(id=id, id_str=id_str, name=name, screen_name=screen_name, followers_count=followers_count,
                        verified=verified, profile_image_url_https=profile_image_url_https, favourites_count=favourites_count)
            db.session.add(user)
            try:
                db.session.commit()
                print('Retweeted User added')
            except sqlIntegrityError:
                db.session.rollback()
                pass

            # retweeted_user = RetweetedUser(
            #     id=id, tweet_id=json_dict['id'])
            # db.session.add(retweeted_user)
            # try:
            #     db.session.commit()
            #     print('Retweeted User added')
            # except sqlIntegrityError:
            #     db.session.rollback()
            #     pass
        except KeyError:
            pass

        # Mentioned Users
        user_mentions = json_dict['entities']['user_mentions']
        for user_mentioned in user_mentions:
            id = user_mentioned['id']
            user_obj = api.get_user(id=id)
            user = User(id=id, id_str=user_obj.id_str, name=user_obj.name, screen_name=user_obj.screen_name, followers_count=user_obj.followers_count,
                        verified=user_obj.verified, profile_image_url_https=user_obj.profile_image_url_https, favourites_count=user_obj.favourites_count)
            db.session.add(user)
            try:
                db.session.commit()
                print('Retweeted User added')
            except sqlIntegrityError:
                db.session.rollback()
                pass
        print('Mentioned Users added')

        # print(tweet)
        for tag in hashtag_models:
            tweet_hashtag = TweetHashtag(
                tweet_id=json_dict['id'], hashtag=tag.hashtag)
            db.session.add(tweet_hashtag)
            try:
                db.session.commit()
            except sqlIntegrityError:
                db.session.rollback()
                pass
        print('Tweet Hashtags Added')
