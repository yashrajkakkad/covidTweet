# import sqlalchemy as db
# from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Table, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import mapper
from vTweet import db
# from app.db import Column, Integer, String, BigInteger, Boolean, DateTime, Table, ForeignKey
# Base = declarative_base()


tweet_hashtag_table = db.Table('tweet_hashtag_table', db.Model.metadata, db.Column('tweet_id', db.Integer, db.ForeignKey(
    'base_tweets.tweet_id')), db.Column('hashtag', db.String(50), db.ForeignKey('hashtags.hashtag')))

# tweet_users = db.Table('tweet_users', db.Model.metadata, db.Column('user_id', db.BigInteger, db.ForeignKey(
#     'users.id')), db.Column('tweet_id', db.BigInteger, db.ForeignKey(
#         'base_tweets.tweet_id')))

# retweeted_users = db.Table('retweeted_users', db.Model.metadata, db.Column('user_id', db.BigInteger, db.ForeignKey(
#     'users.id')), db.Column('tweet_id', db.BigInteger, db.ForeignKey(
#         'base_tweets.tweet_id')))

# mentioned_users = db.Table('mentioned_users', db.Model.metadata, db.Column('user_id', db.BigInteger, db.ForeignKey(
#     'users.id')), db.Column('tweet_id', db.BigInteger, db.ForeignKey(
#         'base_tweets.tweet_id')))


class Hashtag(db.Model):
    __tablename__ = 'hashtags'
    hashtag = db.Column(db.String(50), primary_key=True)


class Place(db.Model):
    __tablename__ = 'places'
    place_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50))
    country = db.Column(db.String(50))
    country_code = db.Column(db.String(5))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)
    id_str = db.Column(db.String(20))
    name = db.Column(db.String(60))
    screen_name = db.Column(db.String(60))
    followers_count = db.Column(db.Integer)
    verified = db.Column(db.Boolean)
    profile_image_url_https = db.Column(db.String(512))
    favourites_count = db.Column(db.Integer)
    # user_type = db.Column(postgresql.ENUM(
    #     'tweet_user', 'retweeted_user', 'mentioned_user', name='user_type_enum'))
    tweets = db.relationship(
        'BaseTweet', secondary='tweet_users', backref='tweet_users')
    retweets = db.relationship(
        'BaseTweet', secondary='retweeted_users', backref='retweeted_users')
    mentioned_tweets = db.relationship(
        'BaseTweet', secondary='mentioned_users', backref='mentioned_users')

    # __mapper_args__ = {
    #     "polymorphic_identity": "person",
    #     "polymorphic_on": user_type,
    # }


class BaseTweet(db.Model):
    __tablename__ = 'base_tweets'
    tweet_id = db.Column(db.BigInteger, primary_key=True)
    tweet_id_str = db.Column(db.String(20))
    source = db.Column(db.String(512))
    favorited = db.Column(db.Boolean)
    retweeted = db.Column(db.Boolean)
    favorite_count = db.Column(db.Integer)
    retweet_count = db.Column(db.Integer)
    result_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    lang = db.Column(db.String(10))
    possibly_sensitive = db.Column(db.Boolean)
    reply_count = db.Column(db.Integer)
    place_id = db.Column(db.String(20), db.ForeignKey('places.place_id'))
    place = db.relationship('Place', backref='base_tweets')
    hashtags = db.relationship(
        'Hashtag', secondary=tweet_hashtag_table, backref='base_tweets')


class TweetUser(db.Model):
    __tablename__ = 'tweet_users'
    user_id = db.Column(db.BigInteger, db.ForeignKey(
        'users.id'), primary_key=True)
    tweet_id = db.Column(db.BigInteger, db.ForeignKey(
        'base_tweets.tweet_id'), primary_key=True)
    # user = db.relationship('User', back_populates='tweet_users')
    # tweet = db.relationship('BaseTweet', back_populates='tweet_users')
    # __mapper_args__ = {"polymorphic_identity": "tweetuser"}


# mapper(TweetUser, tweet_users)


class RetweetedUser(db.Model):
    __tablename__ = 'retweeted_users'
    user_id = db.Column(db.BigInteger, db.ForeignKey(
        'users.id'), primary_key=True)
    tweet_id = db.Column(db.BigInteger, db.ForeignKey(
        'base_tweets.tweet_id'), primary_key=True)
    # user = db.relationship('User', back_populates='retweeted_users')
    # tweet = db.relationship('BaseTweet', back_populates='retweeted_users')
    # __mapper_args__ = {"polymorphic_identity": "retweetuser"}


# mapper(RetweetedUser, retweeted_users)


class MentionedUser(db.Model):
    __tablename__ = 'mentioned_users'
    user_id = db.Column(db.BigInteger, db.ForeignKey(
        'users.id'), primary_key=True)
    tweet_id = db.Column(db.BigInteger, db.ForeignKey(
        'base_tweets.tweet_id'), primary_key=True)
    # # user = db.relationship('User', back_populates='mentioned_users')
    # tweet = db.relationship('BaseTweet', back_populates='mentioned_users')
    # __mapper_args__ = {"polymorphic_identity": "mentioneduser"}


# mapper(MentionedUser, mentioned_users)


class Database():
    # engine = db.create_engine('postgresql://vtweet:vtweet!#%@localhost/vtweet')

    def __init__(self):
        self.connection = db.engine.connect()
        db.create_all()
        print("DB Instance created")
        print("Tables created")

    # def create_all(self):
    #     # Base.metadata.create_all(self.engine)
    #     db.create_all()
    #     # db.session.commit()

    def generate_create_queries(self, filename='createqueries.sql'):
        # print(CreateTable(Hashtag.__table__))
        # print(CreateTable(Hashtag.__table__))
        with open(filename, 'w') as f:
            f.write(CreateTable(Hashtag.__table__).compile(
                dialect=postgresql.dialect()).__str__())
            f.write('\n')
            f.write(CreateTable(Place.__table__).compile(
                dialect=postgresql.dialect()).__str__())
            f.write('\n')
            f.write(CreateTable(User.__table__).compile(
                dialect=postgresql.dialect()).__str__())
            f.write('\n')
            f.write(CreateTable(BaseTweet.__table__).compile(
                dialect=postgresql.dialect()).__str__())
            f.write('\n')
            f.write(CreateTable(TweetUser.__table__).compile(
                dialect=postgresql.dialect()).__str__())
            f.write('\n')
            f.write(CreateTable(RetweetedUser.__table__).compile(
                dialect=postgresql.dialect()).__str__())
            f.write('\n')
            f.write(CreateTable(MentionedUser.__table__).compile(
                dialect=postgresql.dialect()).__str__())
            f.write('\n')


if __name__ == "__main__":
    database = Database()
    # database.create_all()
    # database.generate_create_queries()
