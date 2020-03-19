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

for tweet in tweepy.Cursor(api.search, q='Google').items(1):
    json_dict = tweet._json
    for key in json_dict.keys():
        print(key, ":", json_dict[str(key)])

for tweet in tweepy.Cursor(api.search, q='Google').items(10):
    # logger.debug(tweet._json)
    json_dict = tweet._json
    # logger.debug(json_dict['created_at'])
    # logger.debug(json_dict['id'])
    # logger.debug(json_dict['truncated'])
    # logger.debug(json_dict['text'])

# GET trends/place demo

AHD_LAT = 23.022505
AHD_LONG = 72.571365

# Returns a single element list
ahd_loc_info = api.trends_closest(AHD_LAT, AHD_LONG)
ahd_woeid = ahd_loc_info[0]['woeid']  # Single element is a dict

# Returns a single element list
ahd_trends = api.trends_place(id=str(ahd_woeid))
ahd_trends = ahd_trends[0]['trends']  # Retrieve only the trends
for trend in ahd_trends:
    print(trend['name'])

# Filter search by location

SF_LAT = 37.781157
SF_LONG = -122.398720

NY_LAT = 40.712776
NY_LONG = -74.005974

BENG_LAT = 12.971599
BENG_LONG = 77.594566

# May not work for Gujarati cities. Not enough people posting with location info

geocode = str(BENG_LAT) + ',' + str(BENG_LONG) + ',1mi'

for tweet in tweepy.Cursor(api.search, q='Corona', geocode=geocode).items(10):
    json_dict = tweet._json
    print(json_dict['text'])
    try:
        print(json_dict['place']['name'], '\n')
    except TypeError:
        print('No Location\n')
