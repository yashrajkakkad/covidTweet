from flask import render_template, request, redirect, url_for
from vTweet.views import get_tweets
from vTweet import app


@app.route('/', methods=['GET', 'POST'])
def home():
    # print(url_for())
    if request.method == 'POST':
        query = request.form['query']
        print(get_tweets(query))
        return redirect('/mapdemo')
    return render_template('index.html')


@app.route('/mapdemo', methods=['GET'])
def renderMap():
    return render_template('map.html')
