import tweepy
import logging
from decouple import config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logfile_handler = logging.FileHandler('vTweet.log', mode='w')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logfile_handler.setFormatter(formatter)
logger.addHandler(logfile_handler)

# auth = tweepy.OAuthHandler(config('CONSUMER_KEY'), config('CONSUMER_SECRET'))

# try:
#     redirect_url = auth.get_authorization_url()
# except tweepy.TweepError:
#     print('Error! Failed to get request token.')

# OAuth 2
auth = tweepy.OAuthHandler(config('CONSUMER_KEY'), config('CONSUMER_SECRET'))
api = tweepy.API(auth)

for tweet in tweepy.Cursor(api.search, q='Google').items(1):
    json_dict = tweet._json
    for key in json_dict.keys():
        # logger.debug(key)
        logger.debug(key)
        logger.debug(json_dict[str(key)])

for tweet in tweepy.Cursor(api.search, q='Google').items(10):
    # logger.debug(tweet._json)
    json_dict = tweet._json
    # logger.debug(json_dict['created_at'])
    # logger.debug(json_dict['id'])
    # logger.debug(json_dict['truncated'])
    # logger.debug(json_dict['text'])
