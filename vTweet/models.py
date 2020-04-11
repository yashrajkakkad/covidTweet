# import sqlalchemy as db
# from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Table, ForeignKey
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import mapper
from vTweet import db


class Hashtag(db.Model):
    __tablename__ = 'hashtags'
    hashtag = db.Column(db.String(50), primary_key=True)
    frequency = db.Column(db.Integer)


class Place(db.Model):
    __tablename__ = 'places'
    place_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    country_code = db.Column(
        db.String(5), db.ForeignKey('countries.country_code'))
   # country_code = db.Column(
    #     db.String(5), db.ForeignKey('coordinates.country_code'))
    # coordinates = db.relationship("Coordinates", backref='places')


class Country(db.Model):
    __tablename__ = "countries"
    country_code = db.Column(
        db.String(5), primary_key=True)
    country = db.Column(db.String(50))


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
    tweet_text = db.Column(db.Text)
    source = db.Column(db.String(512))
    favorited = db.Column(db.Boolean)
    retweeted = db.Column(db.Boolean)
    favorite_count = db.Column(db.Integer)
    retweet_count = db.Column(db.Integer)
    result_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    lang = db.Column(db.String(10))
    possibly_sensitive = db.Column(db.Boolean)
    place_id = db.Column(db.String(20), db.ForeignKey('places.place_id'))
    place = db.relationship('Place', backref='base_tweets')
    hashtags = db.relationship(
        'Hashtag', secondary='tweet_hashtag', backref='base_tweets')


class TweetUser(db.Model):
    __tablename__ = 'tweet_users'
    user_id = db.Column(db.BigInteger, db.ForeignKey(
        'users.id'), primary_key=True)
    tweet_id = db.Column(db.BigInteger, db.ForeignKey(
        'base_tweets.tweet_id'), primary_key=True)
    # user = db.relationship('User', back_populates='tweet_users')
    # tweet = db.relationship('BaseTweet', back_populates='tweet_users')
    # __mapper_args__ = {"polymorphic_identity": "tweetuser"}


class RetweetedUser(db.Model):
    __tablename__ = 'retweeted_users'
    user_id = db.Column(db.BigInteger, db.ForeignKey(
        'users.id'), primary_key=True)
    tweet_id = db.Column(db.BigInteger, db.ForeignKey(
        'base_tweets.tweet_id'), primary_key=True)
    # user = db.relationship('User', back_populates='retweeted_users')
    # tweet = db.relationship('BaseTweet', back_populates='retweeted_users')
    # __mapper_args__ = {"polymorphic_identity": "retweetuser"}


class MentionedUser(db.Model):
    __tablename__ = 'mentioned_users'
    user_id = db.Column(db.BigInteger, db.ForeignKey(
        'users.id'), primary_key=True)
    tweet_id = db.Column(db.BigInteger, db.ForeignKey(
        'base_tweets.tweet_id'), primary_key=True)
    # # user = db.relationship('User', back_populates='mentioned_users')
    # tweet = db.relationship('BaseTweet', back_populates='mentioned_users')
    # __mapper_args__ = {"polymorphic_identity": "mentioneduser"}


class TweetHashtag(db.Model):
    __tablename__ = 'tweet_hashtag'
    tweet_id = db.Column(db.BigInteger, db.ForeignKey(
        'base_tweets.tweet_id'), primary_key=True)
    hashtag = db.Column(db.String(50), db.ForeignKey(
        'hashtags.hashtag'), primary_key=True)
    tweet_id_relationship = db.relationship(BaseTweet, backref='tweet_hashtag')
    hashtag_relationship = db.relationship(Hashtag, backref='tweet_hashtag')


# class Coordinates(db.Model):
#     __tablename__ = "coordinates"
#     place_id = db.Column(db.String(20), db.ForeignKey(
#         'places.place_id'), primary_key=True)
#     # country_code = db.Column(db.String(5), primary_key=True)
#     latitude = db.Column(db.Float)
#     longitude = db.Column(db.Float)
#     # place = db.relationship("Place", uselist=False,
#     #                         backref='coordinates')
#     # child = relationship("Child", uselist=False, back_populates="parent")


class Intensity(db.Model):
    __tablename__ = 'intensity'
    latitude = db.Column(db.Float, primary_key=True)
    longitude = db.Column(db.Float, primary_key=True)
    intensity = db.Column(db.Float)


class Database():

    def __init__(self):
        self.connection = db.engine.connect()
        # db.drop_all()
        db.create_all()
        print("DB Instance created")
        print("Tables created")

    def generate_create_queries(self, filename='createqueries.sql'):
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
            f.write(CreateTable(TweetHashtag.__table__).compile(
                dialect=postgresql.dialect()).__str__())
            f.write('\n')
            f.write(CreateTable(Country.__table__).compile(
                dialect=postgresql.dialect()).__str__())
            f.write('\n')
            f.write(CreateTable(Intensity.__table__).compile(
                dialect=postgresql.dialect()).__str__())


if __name__ == "__main__":
    pass
    # database = Database()
    # database.generate_create_queries()
