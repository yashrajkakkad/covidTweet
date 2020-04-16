from flask import render_template, request, redirect, url_for, render_template_string
from sqlalchemy import func
from vTweet.views import insert_tweets_data, fetch_tweet_ids, insert_tweets_from_object
from vTweet import app
from vTweet import db, api
import requests
import pickle
from tweepy.error import TweepError
from wordcloud import WordCloud, STOPWORDS
import preprocessor as p
import re


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
        'SELECT * FROM most_popular_hashtags();').fetchall()

    heatmap_results = db.session.execute(
        'SELECT * FROM heatmap_input();').fetchall()

    popular_user_results = db.session.execute(
        'SELECT * FROM most_popular_users();').fetchall()

    # popular_user_followers = [db.session.execute(
    #     'SELECT * FROM convert_to_human_readable({})'.format(i[2])).scalar() for i in popular_user_results]
    # popular_user_followers = [y[0] for x in popular_user_followers for y in x]
    # popular_user_details = []
    # for
    # for res in popular_user_results:
    #     print(res)
    # for res in popular_user_followers:
    #     print(res)
    # for res in zip(popular_user_followers, popular_user_results):
    #     print(res)

    popular_tweet_results = db.session.execute(
        'SELECT * FROM most_popular_tweets();').fetchall()
    popular_tweet_html = []
    for res in popular_tweet_results:
        # print('https://twitter.com/{}/status/{}'.format(res[1], res[0]))
        r = requests.get('https://publish.twitter.com/oembed', params={
            'url': 'https://twitter.com/{}/status/{}'.format(res[1], res[0])
        })
        # print(type(r))
        # print(r.json())
        try:
            popular_tweet_html.append(r.json()['html'].replace(
                'twitter-tweet', 'twitter-tweet tw-align-center'))
        except KeyError:  # Some accounts have gone private now. Can be made into a trigger possibly
            pass
        # print(r.json()['html'])
    # print(popular_user_followers)
    # for x in popular_user_followers:
    #     for y in x:
    #         print(y)
    # print(popular_user_followers)
    # print(len(popular_user_followers))
    # popular_user_results = [for i in]
    # print(popular_user_results[0])
    # popular_user_results = zip(popular_user_followers, popular_user_results)
    # print(len(popular_user_results))
    # print(popular_user_results)
    # for x,y in popular_user_results:
    #     print(x,y)

    most_positive_tweets = db.session.execute(
        'SELECT * from most_positive_tweets').fetchall()

    print(most_positive_tweets)

    positive_tweets_html = []
    for res in most_positive_tweets:
        # print('https://twitter.com/{}/status/{}'.format(res[1], res[0]))
        r = requests.get('https://publish.twitter.com/oembed', params={
            'url': 'https://twitter.com/{}/status/{}'.format(res[1], res[0])
        })
        # print(type(r))
        # print(r.json())
        try:
            positive_tweets_html.append(r.json()['html'].replace(
                'twitter-tweet', 'twitter-tweet tw-align-center'))
        except KeyError:  # Some accounts have gone private now. Can be made into a trigger possibly
            pass

    most_negative_tweets = db.session.execute(
        'SELECT * from most_negative_tweets').fetchall()

    negative_tweets_html = []
    for res in most_negative_tweets:
        # print('https://twitter.com/{}/status/{}'.format(res[1], res[0]))
        r = requests.get('https://publish.twitter.com/oembed', params={
            'url': 'https://twitter.com/{}/status/{}'.format(res[1], res[0])
        })
        # print(type(r))
        # print(r.json())
        try:
            negative_tweets_html.append(r.json()['html'].replace(
                'twitter-tweet', 'twitter-tweet tw-align-center'))
        except KeyError:  # Some accounts have gone private now. Can be made into a trigger possibly
            pass

    tweets_time_results = db.session.execute('SELECT * FROM tweets_by_time();').scalar()
    print(tweets_time_results)
    return render_template('index.html',
                           hashtag_results=hashtag_results,
                           heatmap_results=heatmap_results,
                           popular_user_results=popular_user_results, popular_tweet_html=popular_tweet_html,
                           positive_tweets_html=positive_tweets_html,
                           negative_tweets_html=negative_tweets_html, tweets_time_results=tweets_time_results)


@app.route('/mapdemo', methods=['GET'])
def renderMap():
    return render_template('map.html')


@app.route('/wordcloud')
def wordcloud_demo():
    words = db.session.execute(
        'SELECT word from tweet_word').fetchall()
    word_list = []
    for word in words:
        word_list.append(word[0])
    word_str = ' '.join(word_list)
    word_str = p.clean(word_str)
    word_str = re.sub(r'[^\x00-\x7F]+', ' ', word_str)
    word_str = word_str.replace('corona', '')
    word_str = word_str.replace('covid', '')
    word_cloud = WordCloud(stopwords=STOPWORDS).generate(word_str)

    # Display the generated image:
    # the matplotlib way:
    import matplotlib.pyplot as plt
    plt.imshow(word_cloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig('GG.png')
    return render_template_string('GG')


@app.route('/fetch')
def fetch():
    tweet_ids = fetch_tweet_ids()
    chunks = [tweet_ids[x:x + 100] for x in range(0, len(tweet_ids), 100)]
    f = open('tweets.pickle', 'ab')
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
    return render_template_string('All tweets fetched into the pickle file')
