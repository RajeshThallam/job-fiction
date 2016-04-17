# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, \
                  jsonify

from app import app
from extract_keywords import extract_keywords as kw
from model_talking import model_talking as mdl
from model_store import model_store as store
import json


# Define the blueprint: 'home', set its url prefix: app.url/home
mod_home = Blueprint('home', __name__, url_prefix='/home')


@mod_home.before_request
def make_session_permanent():
    session.permanent = True

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

    job_query_json = {}
    job_txt = []
    for key, (desc, title) in enumerate(
        zip(job_posts_json['desc'], job_posts_json['title'])):
        job_txt.append(title + ' ' + desc)

    job_query_json['all_jobs'] = job_txt

    print job_query_json
    model = mdl.ModelTalking()
    results = model.get_job_recommendations(job_query_json)

    return jsonify(jobs=results)

# this is utility app to insert model results into Elasticearch
@mod_home.route('/storemodel', methods=['GET', 'POST'])
def store_model_results():
    jobdesc_fname = app.config['STORE_JOBDESC_FILE']
    jobtitle_fname = app.config['STORE_JOBTITLE_FILE']

    es_results = store.ModelStore(jobdesc_fname, jobtitle_fname)
    return_code = es_results.store_results()

    return "Completed storing model results and keywords!!"

# this is utility app to insert model results into Elasticearch
@mod_home.route('/genkwpaths', methods=['GET', 'POST'])
def get_keyword_paths():
    maui = kw.ExtractKeywords()
    maui.generate_keyword_paths()

    return "Completed generating keyword paths!!"