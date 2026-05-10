from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy()

engine = create_engine("mysql+pymysql://root:REDACTED@localhost/mydatabase")
   