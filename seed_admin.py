import os
from app import app
from extensions import db
from models import Administrator
from werkzeug.security import generate_password_hash

with app.app_context():

    username = os.getenv('ADMIN_USERNAME')
    password = os.getenv('ADMIN_PASSWORD')

    if not username or not password:

        print("Error: ADMIN_USERNAME and ADMIN_PASSWORD env vars not set.")
        exit(1)

    existing = Administrator.query.filter_by(username=username).first()

    if not existing:

        admin = Administrator(

            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')

        )

        db.session.add(admin)
        db.session.commit()
        print('Admin created successfully')

    else:

        print('Admin already exists, skipping.')






