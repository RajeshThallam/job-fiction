# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify

from app import app

# Define the blueprint: 'home', set its url prefix: app.url/home
mod_about = Blueprint('about', __name__, url_prefix='/about')


# Set the route and accepted methods
# home page
@mod_about.route('/', methods=['GET', 'POST'])
def about_page():
    return render_template("about/index.html")

# documentation
@mod_about.route('/docs', methods=['GET', 'POST'])
def documentation_page():
    return render_template("about/documentation2.html")
