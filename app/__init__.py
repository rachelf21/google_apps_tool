from flask import Flask
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


from app import routes

# from app.users.routes import users
# app.register_blueprint(users)

