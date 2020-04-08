from flask import render_template, request, redirect, url_for
from sqlalchemy import text
from vTweet.views import insert_tweets_data
from vTweet import app
from vTweet import db


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form['query']
        insert_tweets_data(query)

        # Most popular user
        query = text('select * from most_popular_user()')
        pop_user = db.session.execute(query)  # Has type ResultProxy
        # pop_user = db.session.query(db.func.most_popular_user()).all() Had type list of tuples which were not named tuples
        for user in pop_user:  # Has type RowProxy which is a named tuple
            print(user['name'], user['screen_name'], user['followers_count'])

        # return redirect('/mapdemo')
    return render_template('index.html')


@app.route('/mapdemo', methods=['GET'])
def renderMap():
    return render_template('map.html')
