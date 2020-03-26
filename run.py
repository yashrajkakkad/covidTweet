from vTweet import app, dash_frontend


if __name__ == '__main__':
    app.run(debug=True)
    dash_frontend.run_server(debug=True)
