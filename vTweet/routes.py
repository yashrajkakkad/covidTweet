from flask import render_template, request, redirect, url_for
from vTweet.views import insert_tweets_data
from vTweet import app
from vTweet import db


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form['query']
        insert_tweets_data(query)
        # return redirect('/mapdemo')
    return render_template('index.html')


@app.route('/mapdemo', methods=['GET'])
def renderMap():
    return render_template('map.html')
