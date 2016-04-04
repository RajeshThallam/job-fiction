from app import app
from subprocess import Popen, PIPE, STDOUT
import os
import json
import shutil
import uuid


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

        print self.maui_home
        print path_to_model
        print app.config['ACM_DICT']
        print path_to_test

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

        print results
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
        print "Running MAUI test"
        response= json.loads(
            self.test_maui(maui_workbench, app.config['MODEL_KEYWORDS_ID'], 40)
            )
        print "Completed MAUI test"
        # remove the working directory
        shutil.rmtree(maui_workbench)
        
        print "Prettying up!!"
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

            results[key]=keywords
        
        return json.dumps(results)
