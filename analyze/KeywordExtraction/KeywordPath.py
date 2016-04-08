
# coding: utf-8

# # ACM Taxonomy converter
# 
# We convert the flat file from ACM Taxonomy into a JSON file. Each line contains the keyword and the path that represent the categories and subcategories of this keyword.

# In[175]:

import os,re,json
def generatePathToKeyword():
    pathToMaui="/root/job-fiction/analyze/Keyword Extraction/"
    os.chdir(pathToMaui)
    with open("ACMTaxonomyFlat.txt",'rb') as f:
        path=[]
        level=0
        previousLabel=""
        paths={}

        #We want to construct a dictionary with  Keyword as key and pathToKeyword as value
        for line in f.readlines():
            lineLevel=len(re.findall('@#!',line)) #lineLevel represents the level of the currently processed label
            label= line.split("@#!")[-1].replace("\n","") # extracts the label
            if lineLevel>level: #Going up  a level
                level=lineLevel
                path.append(previousLabel)
                paths[label]= [i for i in path]
            elif lineLevel==level: #Same level
                paths[label]= [i for i in path]
            else:
                diff=level-lineLevel #Going down one or multiple level
                for i in range(diff):
                    level-=1
                    path.pop() 
                paths[label]= [i for i in path]

            previousLabel=label


    with open("ACMTaxonomyPaths.txt","wb")as f2:
        f2.write(json.dumps(paths))

#generatePathToKeyword()

# # Which Path?
# Given a list of keywords, this function calculates the count of each level 1 and level 2 categories.

# In[164]:

import json
from collections import defaultdict  

def whichPath(keywords):
    kwPaths={}
    with open("/root/job-fiction/analyze/Keyword Extraction/ACMTaxonomyPaths.txt","rb")as f:
        allPaths=json.loads(f.read())
        
    #First get the path of each keyword from the file that we generate previously.
    for i in keywords:
        i=i.strip()
        try:
            kwPaths[i]=allPaths[i]
        except:
            kwPaths[i]=["Others"]
    
    #For all keywords we compute the total number level 1 and level 2 categories
    level2Cat= defaultdict(int)
    level1Cat= defaultdict(int)
    categories={}
    
    for k,v in kwPaths.iteritems():
        
        if v[0] not in categories.keys():
            categories[v[0]]={}
            categories[v[0]]["count"]=1
        else:
            categories[v[0]]["count"]+=1
        try:
            if v[1] not in categories[v[0]].keys():
                categories[v[0]][v[1]]=1
            else:
                categories[v[0]][v[1]]+=1   
        except:
            print "categories 'Other' encountered"
        
    return categories
    
    
#print whichPath(['Secure Sockets Layer',"Die and wafer stacking","Anthropology","Semantic networks","Network on chip"
           ,"System on a chip","Stack machines","Parallel architectures","cookie"])



