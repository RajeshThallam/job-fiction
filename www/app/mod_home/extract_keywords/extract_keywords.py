from subprocess import Popen, PIPE, STDOUT
from collections import defaultdict  
from app import app
import shutil
import json
import uuid
import re
import os


class ExtractKeywords(object):
    def __init__(self):
        self.maui_home = app.config['MAUI_HOME_PATH']

    # Function to train a MAUI model.
    # Input:
    # - path to training file,
    # - suffix so we can generate our own model
    # - minimum number of occurence
    # Output:
    # - path to model file

    def train_maui(self, path_to_train, model_id, min_occurence):
        path_to_model = app.config['MODEL_KEYWORDS_DIR'] + model_id

        p = Popen(["java", "-jar", "-Xmx1024m", self.maui_home, 
            "train", "-l", path_to_train, "-m", path_to_model,
            "-v", app.config['ACM_EXTENDED_DICT'], 
            "-f", "skos", "-o",str(minOccurence)], 
            stdout=PIPE, stderr=STDOUT
            )

        for line in p.stdout:
            if line.find("WARN"):
                continue
            print line

        return path_to_model


    # Function to test a MAUI model. 
    # Input: 
    # - path to test file, 
    # - modelID for differenting models (so we can work on different model)
    # - maximum number of keywords to return
    # Output:
    # - A JSON containing the keywords

    def test_maui(self, path_to_test, model_id, num_keywords):
        path_to_model = os.path.join(app.config['MODEL_KEYWORDS_DIR'], model_id)
        results = {}
        kw = {}
        doc = ""
        init = 0

        p = Popen(["java", "-jar", "-Xmx1024m", self.maui_home, 
            "test", "-l", path_to_test, "-m", path_to_model,
            "-v", app.config['ACM_DICT'], 
            "-f","skos","-n",str(num_keywords)], 
            stdout=PIPE, stderr=STDOUT
            )

        gen=(line for line in p.stdout if line.find("MauiTopicExtractor")<>-1 )

        for line in gen:
            if line.find("Processing document")<>-1:
                #open a new doc
                doc = line.split("Processing document: ")[-1].split("\n")[0]
                kw={}
                continue

            elif line.find("Topic ")<>-1:
                key=line.split("Topic ")[-1].split( " 1 ")[0]
                
                #removing . because mongodb does not like dot in keys
                key=key.replace("."," ")

                value=line.split( " 1 ")[-1].split(" > ")[0]
                kw[key]=value
                init=1

            if init:
                results[doc]=kw

        return json.dumps(results)


    # Function takes a JSON, save it into a directory and call the testMaui function.
    # Query should be in the form of {"jobID1":"summary","jobID2":"summary2",...}

    def find_keywords(self, query, thresholds = [0.6, 0.2]):
        # unique directory for every request
        maui_workbench = os.path.join(os.getcwd(), 
            "workbench", 
            str(uuid.uuid1()))

        # create a temporary directory for MAUI to work in
        if not os.path.exists(maui_workbench):
            os.makedirs(maui_workbench)

        # load the query and split each document into a separate file
        data = query

        for k, v in data.iteritems():
            with open(os.path.join(maui_workbench, k + ".txt"), 'w') as recFile:
                recFile.write(v)

        # call the Maui wrapper on these files
        print "Running MAUI test @" + maui_workbench
        response= json.loads(
            self.test_maui(maui_workbench, app.config['MODEL_KEYWORDS_ID'], 40)
            )
        print "Completed MAUI test @" + maui_workbench
        # remove the working directory
        shutil.rmtree(maui_workbench)
        
        # generate pretty results
        results={}
        for k,v in response.iteritems():
            key = k.split(".txt")[0]

            mustHave = {}
            niceHave = {}
            exclude = {}
            keywords = {}

            for k2,v2 in v.iteritems():    
                if float(v2) > thresholds[0]:
                    mustHave[k2] = float(v2)
                elif float(v2) > thresholds[1]:
                    niceHave[k2] = float(v2)
                else:
                    exclude[k2] = float(v2)

                keywords['must_have'] = mustHave
                keywords['nice_have'] = niceHave
                keywords['excluded'] = exclude

            results[key] = keywords
        
        # get categories and append to keywords
        all_keywords = \
            results['all_jobs']['must_have'].keys() + \
            results['all_jobs']['nice_have'].keys()

        results['all_jobs']['categories'] = self.get_categories(all_keywords)

        print results

        return json.dumps(results)


    # ACM Taxonomy converter
    # We convert the flat file from ACM Taxonomy into a JSON file. Each line 
    # contains the keyword and the path that represent the categories and 
    # subcategories of this keyword.

    def generate_keyword_paths(self):
        path = []
        level = 0
        previousLabel = ""
        paths = {}

        with open(app.config['ACM_TAXONOMY_TEXT'],'rb') as f:
            # construct dict with key: Keyword and value: pathToKeyword
            for line in f.readlines():
                # lineLevel represents the level of the currently processed label
                lineLevel = len(re.findall('@#!',line)) 
                # extracts the label
                label = line.split("@#!")[-1].replace("\n","") 

                # going up  a level
                if lineLevel > level: 
                    level = lineLevel
                    path.append(previousLabel)
                    paths[label] = [i for i in path]
                # same level
                elif lineLevel == level:
                    paths[label] = [i for i in path]
                # going down one or multiple level
                else:
                    diff = level - lineLevel 
                    for i in range(diff):
                        level -= 1
                        path.pop() 
                    paths[label] = [i for i in path]

                previousLabel = label

        with open(app.config['ACM_TAXONOMY_PATH'], "wb")as f2:
            f2.write(json.dumps(paths))


    # given a list of keywords, this function calculates the count of each 
    # level 1 and level 2 categories in ACM taxonomy

    def get_categories(self, keywords):
        kwPaths = {}

        with open(app.config['ACM_TAXONOMY_PATH'], "rb")as f:
            allPaths=json.loads(f.read())
            
        # get the path of each keyword from the file generated previously
        for i in keywords:
            i=i.strip()
            try:
                kwPaths[i] = allPaths[i]
            except:
                kwPaths[i] = ["Others"]
        
        # for all keywords, compute the total level 1 and level 2 categories
        level2Cat = defaultdict(int)
        level1Cat = defaultdict(int)
        categories = {}
        
        for k,v in kwPaths.iteritems():
            
            if v[0] not in categories.keys():
                categories[v[0]] = {}
                categories[v[0]]["count"] = 1
            else:
                categories[v[0]]["count"] += 1

            try:
                if v[1] not in categories[v[0]].keys():
                    categories[v[0]][v[1]] = 1
                else:
                    categories[v[0]][v[1]] += 1   
            except:
                print "categories 'Other' encountered"
            
        return categories
