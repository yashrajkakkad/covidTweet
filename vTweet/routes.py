from flask import render_template, request, redirect, url_for
from vTweet.views import get_tweets
from vTweet.models import Hashtag
from vTweet import app
from vTweet import db
# from sqlalchemy.orm import sessionmaker

# Session = sessionmaker(bind=db.engine)
# session = Session()


@app.route('/', methods=['GET', 'POST'])
def home():
    # print(url_for())
    if request.method == 'POST':
        query = request.form['query']
        get_tweets(query)
        # hashtags = get_tweets(query)
        # tags = [Hashtag(hashtag=hashtags[i]['text'])
        #         for i in range(len(hashtags))]
        # for tag in tags:
        #     print(tag.hashtag)
        #     session.add(tag)
        # session.commit()
        return redirect('/mapdemo')
    return render_template('index.html')


@app.route('/mapdemo', methods=['GET'])
def renderMap():
    return render_template('map.html')
