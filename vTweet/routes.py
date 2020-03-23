from flask import render_template, request
from vTweet.views import get_tweets
from vTweet import app


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form['query']
        print(get_tweets(query))
    return render_template('index.html')
