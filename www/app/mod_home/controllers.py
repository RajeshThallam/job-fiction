# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify

from app import app
from run_scripts import RunThread
import json


# Define the blueprint: 'home', set its url prefix: app.url/home
mod_home = Blueprint('home', __name__, url_prefix='/home')


# Set the route and accepted methods
# home page
@mod_home.route('/', methods=['GET', 'POST'])
def home_page():
    return render_template("home/index.html")


# get keywords for the jobs descriptions submitted by user
@mod_home.route('/getkeywords', methods=['GET', 'POST'])
def get_keywords():
    # read url parameters
    job_posts = request.args.get('jobposts')

    # set parameters to call keyword extraction module
    params = [app.config['EXTRACT_KEYWORDS'], job_posts]

    # launch script and capture output
    thread = RunThread(params)
    thread.start()
    thread.join()
    keywords = json.loads(thread.stdout)

    return jsonify(keywords)