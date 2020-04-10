from flask import render_template, request, redirect, url_for, render_template_string
from sqlalchemy import text
from vTweet.views import insert_tweets_data, fetch_tweet_ids, insert_tweets_from_object
from vTweet import app
from vTweet import db, api
import pickle


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
    return render_template('index.html')


@app.route('/mapdemo', methods=['GET'])
def renderMap():
    return render_template('map.html')


@app.route('/fetch')
def fetch():
    tweet_ids = fetch_tweet_ids()
    chunks = [tweet_ids[x:x + 100] for x in range(0, len(tweet_ids), 100)]
    f = open('tweets.pickle', 'wb')
    for chunk in chunks:
        statuses = api.statuses_lookup(chunk, include_entities=True)
        for status in statuses:
            pickle.dump(status, f)
            # print(type(status))
            # print(status)
            # insert_tweets_from_object(status)
    return render_template_string('Hello')
