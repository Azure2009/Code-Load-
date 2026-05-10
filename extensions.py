from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy()

engine = create_engine("mysql+pymysql://root:0920juancarlo@localhost/mydatabase")
   