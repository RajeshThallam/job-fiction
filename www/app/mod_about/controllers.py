# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify

from app import app

# Define the blueprint: 'home', set its url prefix: app.url/home
mod_landing = Blueprint('landing', __name__, url_prefix='/landing')


# Set the route and accepted methods
# home page
@mod_landing.route('/', methods=['GET', 'POST'])
def landing_page():
    return render_template("landing/index.html")
