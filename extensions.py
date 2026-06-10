from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from functools import wraps
from flask import make_response

db = SQLAlchemy()

engine = create_engine("mysql+pymysql://root:0920juancarlo@localhost/mydatabase")

def nocache(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated