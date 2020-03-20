from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Table, ForeignKey, Base

tweet_hashtag_table = Table('tweet_hashtag_table', Base.metadata, Column('tweet_id', Integer, ForeignKey('tweets.tweet_id')), Column('hashtag', String(50), ForeignKey('hashtags.hashtag')))

class Hashtag(Base):
    __tablename__ = 'hashtags'
    hashtag = Column(String(50), primary_key=True)

class Place(Base):
    __tablename__ = 'places'
    place_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    country = Column(String(50))
    country_code = Column(String(5))

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    id_str = Column(String(20))
    name = Column(String(60))
    screen_name = Column(String(60))
    followers_count = Column(Integer)
    verified = Column(Boolean)
    profile_image_url_https = Column(String(512))
    favourites_count = Column(Integer)

class TweetUser(User):
    __tablename__ = 'tweet_users'

class RetweetedUser(User):
    __tablename__ = 'retweeted_users'

class MentionedUser(User):
    __tablename__ = 'mentioned_users'

class BaseTweet(Base):
    __tablename__ = 'base_tweets'
    tweet_id = Column(BigInteger, primary_key=True)
    tweet_id_str = Column(String(20))
    source = Column(String(512))
    favorited = Column(Boolean)
    retweeted = Column(Boolean)
    favorite_count = Column(Integer)
    retweet_count = Column(Integer)
    result_type = Column(String(20))
    created_at = Column(DateTime)
    lang = Column(String(10))
    possibly_sensitive = Column(Boolean)
    reply_count = Column(Integer)

