# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify

from app import app
from run_scripts import RunThread
from extract_keywords import extract_keywords as kw
from model_talking import model_talking as mdl
import json
import ast


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
    job_posts = request.get_data().decode('utf-8')
    job_posts_json = json.loads(job_posts)

    job_desc_json = {}
    job_desc_txt = ""
    for key, desc in enumerate(job_posts_json['desc']):
        job_desc_txt += desc
        #job_desc_json[ 'job_' + str(key+1)] = desc.encode('utf-8')

    job_desc_json['all_jobs'] = job_desc_txt.encode('utf-8')

    print job_desc_json
    maui = kw.ExtractKeywords()
    keywords = json.loads(maui.find_keywords(job_desc_json))
    print keywords['all_jobs']

    return jsonify(keywords['all_jobs'])

# get job results based on the dream job description and preferences of user
@mod_home.route('/getresults', methods=['GET', 'POST'])
def get_results():
    # read url parameters
    job_posts = request.get_data().decode('utf-8')
    job_posts_json = json.loads(job_posts)

    job_desc_json = {}
    job_desc_txt = ""
    for key, desc in enumerate(job_posts_json['desc']):
        job_desc_txt += desc

    job_desc_json['all_jobs'] = job_desc_txt.encode('utf-8')

    print job_desc_json
    model = mdl.ModelTalking()
    results = json.loads(model.get_job_recommendations(job_desc_json))
    print results

    return jsonify(results)