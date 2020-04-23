from flask import render_template, request, redirect, url_for, render_template_string
from sqlalchemy import func
from vTweet.views import insert_tweets_data, fetch_tweet_ids, insert_tweets_from_object
from vTweet import app
from vTweet import db, api
import requests
import pickle
from tweepy.error import TweepError
from shutil import copyfile


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
        'SELECT * from most_positive_tweets()').fetchall()

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
        'SELECT * from most_negative_tweets()').fetchall()

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

    tweets_time_results = db.session.execute(
        'SELECT * FROM tweets_by_time_with_sentiment();').fetchall()

    generate_wordcloud = None
    # generate_wordcloud = db.session.execute(
    #     'SELECT * from generate_word_cloud(ARRAY(select word from tweet_word), ARRAY(select word from tweet_word_sentiment where score > 0), ARRAY(select word from tweet_word_sentiment where score < 0));')
    # copyfile('/var/lib/postgres/data/cloud.png', 'vTweet/static/images/cloud.png')
    # copyfile('/var/lib/postgres/data/pos_cloud.png', 'vTweet/static/images/pos_cloud.png')
    # copyfile('/var/lib/postgres/data/neg_cloud.png', 'vTweet/static/images/neg_cloud.png')
    tweets_time_results = tweets_time_results[0]

    activity_hours_by_place = db.session.execute(
        'SELECT * FROM most_active_time_per_location();').fetchall()

    mean_sentiment_scores_by_location = db.session.execute(
        'SELECT * FROM mean_sentiment_scores_by_location();').fetchall()

    max_min_mean_scores = db.session.execute(
        'SELECT * FROM max_min_mean_sentiment_scores();').fetchall()

    normalized_mean_sentiment_scores = []
    for res in mean_sentiment_scores_by_location:
        normalized_mean_sentiment_scores.append(translate(float(res[2]), float(
            max_min_mean_scores[1][0]), float(max_min_mean_scores[0][0]), 0, 1))

    return render_template('index.html',
                           hashtag_results=hashtag_results,
                           heatmap_results=heatmap_results,
                           popular_user_results=popular_user_results, popular_tweet_html=popular_tweet_html,
                           positive_tweets_html=positive_tweets_html,
                           negative_tweets_html=negative_tweets_html,
                           tweets_time_results=tweets_time_results,
                           activity_hours_by_place=activity_hours_by_place,
                           mean_sentiment_scores_by_location=mean_sentiment_scores_by_location, normalized_mean_sentiment_scores=normalized_mean_sentiment_scores)


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


@app.route('/log')
def log():
    logger_results = db.session.execute(
        'SELECT * FROM log ORDER BY datetime DESC;')
    return render_template('log.html',
                           logger_results=logger_results)


@app.route('/delete', methods=['GET', 'POST'])
def delete_tweet():
    if request.method == 'POST':
        tweet_id = request.form['tweet_id']
        db.session.execute(
            'CALL fetch_data_to_be_deleted({});'.format(tweet_id))
        tbd_data = db.session.execute('SELECT * FROM tbd_data;')
        db.session.execute('DELETE FROM tbd_data WHERE TRUE;')
        # Commiting this way also commits the subsequent delete operations
        db.session.execute(
            'BEGIN; DELETE FROM base_tweets WHERE base_tweets.tweet_id={}; COMMIT;'.format(tweet_id))
        return render_template('delete_tweet_success.html',
                               tweet_id=tweet_id,
                               tbd_data=tbd_data)
    return render_template('delete_tweet.html')


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


@app.route('/insert', methods=['GET', 'POST'])
def insert():
    alert_message = None
    green_message = None
    if request.method == 'POST':
        tweet_id = request.form['tweet_id']
        try:
            status = api.statuses_lookup([tweet_id], include_entities=True)
            if len(status) == 0:
                raise Exception('No tweet')
            try:
                print(type(status))
                print(status)
                insert_tweets_from_object(status[0])
                green_message = 'Tweet inserted successfully'
            except Exception:
                alert_message = 'Something went wrong while inserting the tweet in the database'
        except Exception:
            alert_message = 'Invalid Tweet ID / Connectivity issue'
    return render_template('insert.html', alert_message=alert_message, green_message=green_message)


@app.route('/sentiment')
def sentiment():
    db.session.execute(
        'BEGIN; DELETE FROM tweet_word_sentiment; DELETE FROM tweet_word; COMMIT;')
    # db.session.execute('')
    db.session.execute('CALL remove_special_characters();')
    db.session.execute('CALL calculate_word_score();')
    db.session.commit()
    return render_template('sentiment.html')
