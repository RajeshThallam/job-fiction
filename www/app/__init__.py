# Import flask and template operators
from flask import Flask, render_template

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    #return render_template('404.html'), 404
    return "Oops!! It's 404. Page doesn't exist."

# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_home.controllers import mod_home as auth_home

# Register blueprint(s)
app.register_blueprint(auth_home)