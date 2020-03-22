from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vtweet:vtweet!#%@localhost/vtweet'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        print(request.form['query'])

    return render_template('index.html')