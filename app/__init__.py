from flask import Flask
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


from app import routes

from app.photos.routes import photos
app.register_blueprint(photos)

