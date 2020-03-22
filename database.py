# import sqlalchemy as db
# from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Table, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from app import db

# from app.db import Column, Integer, String, BigInteger, Boolean, DateTime, Table, ForeignKey
# Base = declarative_base()
    

tweet_hashtag_table = db.Table('tweet_hashtag_table', db.Model.metadata, db.Column('tweet_id', db.Integer, db.ForeignKey('tweets.tweet_id')), db.Column('hashtag', db.String(50), db.ForeignKey('hashtags.hashtag')))


class Hashtag(db.Model):
    __tablename__ = 'hashtags'
    hashtag = db.Column(db.String(50), primary_key=True)

class Place(db.Model):
    __tablename__ = 'places'
    place_id = db.Column(db.Integer, primary_key=True)
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
    place_id = db.Column(db.Integer, db.ForeignKey('places.place_id'))
    place = db.relationship('Place', back_populates='base_tweets')


class TweetUser(User):
    __tablename__ = 'tweet_users'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), primary_key=True)
    tweet_id = db.Column(db.BigInteger, db.ForeignKey('base_tweets.tweet_id'), primary_key=True)
    user = db.relationship('User', back_populates='tweet_users')
    tweet = db.relationship('BaseTweet', back_populates='tweet_users')


class RetweetedUser(User):
    __tablename__ = 'retweeted_users'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), primary_key=True)
    tweet_id = db.Column(db.BigInteger, db.ForeignKey('base_tweets.tweet_id'), primary_key=True)
    user = db.relationship('User', back_populates='retweeted_users')
    tweet = db.relationship('BaseTweet', back_populates='retweeted_users')

class MentionedUser(User):
    __tablename__ = 'mentioned_users'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), primary_key=True)
    tweet_id = db.Column(db.BigInteger, db.ForeignKey('base_tweets.tweet_id'), primary_key=True)
    user = db.relationship('User', back_populates='mentioned_users')
    tweet = db.relationship('BaseTweet', back_populates='mentioned_users')

class Database():
    # engine = db.create_engine('postgresql://vtweet:vtweet!#%@localhost/vtweet')

    def __init__(self):
        self.connection = db.engine.connect()
        print("DB Instance created")

    def create_all(self):
        # Base.metadata.create_all(self.engine)
        db.create_all()
        print("Tables created")
    
    def generate_create_queries(self, filename='createqueries.sql'):
        # print(CreateTable(Hashtag.__table__))
        # print(CreateTable(Hashtag.__table__))
        with open(filename, 'w') as f:
            f.write(CreateTable(Hashtag.__table__).compile(dialect=postgresql.dialect()).__str__())
            f.write('\n')            
            f.write(CreateTable(Place.__table__).compile(dialect=postgresql.dialect()).__str__())
            f.write('\n')            
            f.write(CreateTable(User.__table__).compile(dialect=postgresql.dialect()).__str__())
            f.write('\n')            
            f.write(CreateTable(BaseTweet.__table__).compile(dialect=postgresql.dialect()).__str__())
            f.write('\n')            
            f.write(CreateTable(TweetUser.__table__).compile(dialect=postgresql.dialect()).__str__())
            f.write('\n')            
            f.write(CreateTable(RetweetedUser.__table__).compile(dialect=postgresql.dialect()).__str__())
            f.write('\n')
            f.write(CreateTable(MentionedUser.__table__).compile(dialect=postgresql.dialect()).__str__())
            f.write('\n')            
  


if __name__ == "__main__":
    database = Database()
    # database.create_all()
    database.generate_create_queries()    
