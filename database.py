import sqlalchemy as db
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

Base = declarative_base()

    

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
    place_id = Column(Integer, ForeignKey('places.place_id'))
    place = relationship('Place', back_populates='base_tweets')


class TweetUser(User):
    __tablename__ = 'tweet_users'
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    tweet_id = Column(BigInteger, ForeignKey('base_tweets.tweet_id'), primary_key=True)
    user = relationship('User', back_populates='tweet_users')
    tweet = relationship('BaseTweet', back_populates='tweet_users')


class RetweetedUser(User):
    __tablename__ = 'retweeted_users'
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    tweet_id = Column(BigInteger, ForeignKey('base_tweets.tweet_id'), primary_key=True)
    user = relationship('User', back_populates='retweeted_users')
    tweet = relationship('BaseTweet', back_populates='retweeted_users')

class MentionedUser(User):
    __tablename__ = 'mentioned_users'
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    tweet_id = Column(BigInteger, ForeignKey('base_tweets.tweet_id'), primary_key=True)
    user = relationship('User', back_populates='mentioned_users')
    tweet = relationship('BaseTweet', back_populates='mentioned_users')

class Database():
    engine = db.create_engine('postgresql://vtweet:vtweet!#%@localhost/vtweet')

    def __init__(self):
        self.connection = self.engine.connect()
        print("DB Instance created")
    def create_all(self):
        declarative_base().metadata.create_all(self.engine)
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
