from subprocess import Popen, PIPE, STDOUT
import os,time
import json,shutil

pathToMaui="/root/job-fiction/analyze/Keyword Extraction/"
os.chdir(pathToMaui)
# Function to train a MAUI model. 
# Input: 
# - path to training file, 
# - suffix so we can generate our own model
# - minimum number of occurence
# Output:
# - path to model file

def trainMaui(pathToTrain, modelID, minOccurence):
    pathToModel="./data/models/keyword_extraction_model_"+modelID
    p = Popen(["java", "-jar", "-Xmx1024m", "maui-standalone-1.1-SNAPSHOT.jar", 
         "train", "-l",pathToTrain, "-m",pathToModel,
               "-v","ACMTaxonomySkosExtended.rdf","-f","skos","-o",str(minOccurence)], stdout=PIPE, stderr=STDOUT)
    for line in p.stdout:
        if line.find("WARN"):
            continue
        print line
    return pathToModel


# Function to test a MAUI model. 
# Input: 
# - path to test file, 
# - modelID for differenting models (so we can work on different model)
# - maximum number of keywords to return
# Output:
# - A JSON containing the keywords

def testMaui(pathToTest, modelID, numKw):
    pathToModel="./data/models/keyword_extraction_model_"+modelID
    p = Popen(["java", "-jar", "-Xmx1024m", "maui-standalone-1.1-SNAPSHOT.jar", 
         "test", "-l",pathToTest, "-m",pathToModel,
           "-v","ACMTaxonomySkos.rdf","-f","skos","-n",str(numKw)], stdout=PIPE, stderr=STDOUT)
    results={}
    kw={}
    doc=""
    init=0
    
    gen=(line for line in p.stdout if line.find("MauiTopicExtractor")<>-1 )
    for line in gen:
        if line.find("Processing document")<>-1:
            #open a new doc
            doc= line.split("Processing document: ")[-1].split("\n")[0]
            kw={}
            continue

        elif line.find("Topic ")<>-1:
            key=line.split("Topic ")[-1].split( " 1 ")[0]
            
            key=key.replace("."," ")#removing . because mongodb does not like dot in keys

            value=line.split( " 1 ")[-1].split(" > ")[0]
            kw[key]=value
            init=1
        if init:
            results[doc]=kw
    return json.dumps(results)

# Function takes a JSON, save it into a directory and call the testMaui function.
# Query should be in the form of {"jobID1":"summary","jobID2":"summary2",...}
def mauiTopicClf(query,thres1=0.6,thres2=0.2):
    #create a temporary directory for MAUI to work in
    if not os.path.exists("workbench"):
        os.makedirs("workbench")
    # load the query and split each document into a separate file
    data=json.loads(query)
    for k,v in data.iteritems():
        with open("workbench/"+k+".txt",'w') as recFile:
            recFile.write(v)
    # call the Maui wrapper on these files
    response= json.loads(testMaui("workbench", "Steph", 40))
    # remove the working directory
    shutil.rmtree("./workbench")
    

    results={}
    for k,v in response.iteritems():
        key=k.split(".txt")[0]
        mustHave={}
        niceHave={}
        exclude={}
        keywords={}
        for k2,v2 in v.iteritems():    
            if float(v2)>thres1:
                mustHave[k2]=float(v2)
            elif float(v2)>thres2:
                niceHave[k2]=float(v2)
            else:
                exclude[k2]=float(v2)
            keywords['MustHave']= mustHave
            keywords['NiceHave']= niceHave
            keywords['Excluded']= exclude
        results[key]=keywords
    
    return json.dumps(results)
