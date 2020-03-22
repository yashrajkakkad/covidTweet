from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vtweet:vtweet!#%@localhost/vtweet'
db = SQLAlchemy(app)

# Models

@app.route('/')
def home():
    return 'Hello, World!'