from flask import render_template, request, redirect, url_for, render_template_string
from sqlalchemy import func
from vTweet.views import insert_tweets_data, fetch_tweet_ids, insert_tweets_from_object
from vTweet import app
from vTweet import db, api
<<<<<<< HEAD
import requests
=======
import pickle
from tweepy.error import TweepError
>>>>>>> 67c6f69... Added new tables for word sentiment analysis


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form['query']
        insert_tweets_data(query)
        # Most popular user
        # query = text('select * from most_popular_user()')
        # pop_user = db.session.execute(query)  # Has type ResultProxy
        # pop_user = db.session.query(db.func.most_popular_user()).all() Had type list of tuples which were not named tuples
        # for user in pop_user:  # Has type RowProxy which is a named tuple
        # print(user['name'], user['screen_name'], user['followers_count'])

        # return redirect('/mapdemo')
    # result = db.session.query(func.public.most_popular_hashtags()).all()
    hashtag_results = db.session.execute(
        'SELECT * FROM most_popular_hashtags();')

    heatmap_results = db.session.execute('SELECT * FROM heatmap_input();')

    popular_user_results = db.session.execute(
        'SELECT * FROM most_popular_users();')

    popular_tweet_results = db.session.execute('SELECT * FROM most_popular_tweets();')
    popular_tweet_html = []
    for res in popular_tweet_results:
        print(res)
        # print('https://twitter.com/{}/status/{}'.format(res[1], res[0]))
        r = requests.get('https://publish.twitter.com/oembed', params={
            'url': 'https://twitter.com/{}/status/{}'.format(res[1], res[0])
        })
        # print(type(r))
        # print(r.json())
        popular_tweet_html.append(r.json()['html'])
        # print(r.json()['html'])
    return render_template('index.html', hashtag_results=hashtag_results, heatmap_results=heatmap_results,
                           popular_user_results=popular_user_results, popular_tweet_html=popular_tweet_html)


@app.route('/mapdemo', methods=['GET'])
def renderMap():
    return render_template('map.html')


@app.route('/fetch')
def fetch():
    tweet_ids = fetch_tweet_ids()
    chunks = [tweet_ids[x:x + 100] for x in range(0, len(tweet_ids), 100)]
    f = open('tweets.pickle', 'wb')
    for i, chunk in enumerate(chunks):
        try:
            statuses = api.statuses_lookup(chunk, include_entities=True)
            for status in statuses:
                pickle.dump(status, f)
                # print(type(status))
                # print(status)
                # insert_tweets_from_object(status)
        except TweepError:
            pass
        print(i)
    return render_template_string('Hello')
