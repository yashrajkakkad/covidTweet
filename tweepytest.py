import tweepy
from decouple import config

# auth = tweepy.OAuthHandler(config('CONSUMER_KEY'), config('CONSUMER_SECRET'))

# try:
#     redirect_url = auth.get_authorization_url()
# except tweepy.TweepError:
#     print('Error! Failed to get request token.')


# OAuth 2
auth = tweepy.OAuthHandler(config('CONSUMER_KEY'), config('CONSUMER_SECRET'))
api = tweepy.API(auth)
for tweet in tweepy.Cursor(api.search, q='Google').items(10):
    print(tweet)

