import requests
import json
import codecs
from indeed import IndeedClient
from lxml import html
import pymongo
import math
import logging
from datetime import datetime

try:
    conn=pymongo.MongoClient()
    print "Connected!"
except pymongo.errors.ConnectionFailure, e:
   print "Connection failed : %s" % e 
myColl=conn["JOBFICTION"].jobs

#dave's credentials
client = IndeedClient('8525918673571870')
streamLimit=25


def fetch_overview_data(search,location): 
    params = params = {
    'q' : search,
    'l' : location,
    'r': 0,
    'sort': 'date',
    'fromage':1,
    'userip' : "1.2.3.4",
    'useragent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)"
    }
    results=client.search(**params)
    return(results)

def fetch_batch_data(search,location,start): 
    params = params = {
    'q' : search,
    'l' : location,
    'r': 0,
    'sort': 'date',
    'fromage':1,      
    'userip' : "1.2.3.4",
    'useragent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)",
    'limit':streamLimit,
    'latlong':1,
    'start': start*streamLimit
    }
    
    results=client.search(**params)
    return(results)

def parse_jobs(jobs):

    for j in jobs['results']:

        city=j["city"]
        date=j["date"]
        try:
            latitude=j["latitude"]
        except :
            latitude=0
            print "Error loading lat"
        try:
            longitude=j["longitude"]
        except:
            longitude=0
            print "Error loading long"
        url=j["url"]
        jobtitle= j["jobtitle"]
        company= j["company"]
        fullLoc= j["formattedLocationFull"]
        source=j["source"]
        state=j["state"]
        country=j["country"]
        jobkey=j["jobkey"]
        sponsored=j["sponsored"]
        expired=j["expired"]
        indeedApply=j["indeedApply"]
        try:
            summary=get_job_summary(j["url"])
        except Exception as e:
            print e
            logging.warning(e)
            print "Error getting summary"
            continue
        response= myColl.update(
            {'_id': "indeed_"+jobkey},
            {
            "city":city,
            "date":date,
            "latitude":latitude,
            "longitude":longitude,
            "url":url,
            "jobtitle":jobtitle,
            "company":company,
            "fullLoc":fullLoc,
            "source":source,
            "state":state,
            "country":country,
            "jobkey":jobkey,
            "sponsored":sponsored,
            "expired":expired,
            "indeedApply":indeedApply,
            "summary":summary
            },
            upsert=True)
        
        # if not(response['updatedExisting']):
        #     print "inserted job title "+ jobtitle +" "+ jobkey+ " " + date
        # else: 
        #     print "got the same job to insert "+ jobtitle +" "+ jobkey+ " " + date

def get_job_summary(url):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    summary=tree.xpath('//span[@id="job_summary"]//text()')
    return summary

def get_zipcodes():
    import csv
    zipcodes=[]
    with open('zipcode_raj.csv', 'rb') as csvfile:
        next(csvfile,None) # skip header line
        cr = csv.reader(csvfile, delimiter=',')
        for row in cr:
            zipcodes.append(row)
    return zipcodes




query=""
zipcodes=get_zipcodes()
logging.basicConfig(filename='/root/logs/streamRaj.log', level=logging.DEBUG)
logging.info("Starting acquisition. Time= "+ datetime.now().isoformat())


# search is location based, we need to cycle through all the zipcodes in US
for z in zipcodes:
    print("zipcode "+str(z))
    logging.info("Fetching jobs in "+ str(z))
    try:
        overview = fetch_overview_data(query,z)
    except KeyboardInterrupt:
        break
        raise Exception('Streaming Cancelled')
    except Exception as e:
        logging.warning(e)
        print e
        continue
    #print overview
    # print "\n"
    # job_response = client.jobs(jobkeys = ["7fd0bd5a6f2d701b"])
    # print job_response

    num_results = overview['totalResults']
    logging.info("There is "+ str(num_results)+ " in this location.")

    for i in range(int(math.ceil(num_results/streamLimit))+1):
        if i*streamLimit>1000: # we can only gather 1000 jobs in one query batch
            break
        try:
            jobs=fetch_batch_data(query,z,i)
        except KeyboardInterrupt:
            break
            raise Exception('Streaming Cancelled')
        except Exception as e:
            logging.warning(e)
            print e
            continue
        parse_jobs(jobs)
    logging.info("Done fetching jobs in "+ str(z))
    logging.info("Could not retrieve "+ str(max([0,num_results-1000]))+" jobs in zipcode "+ str(z) )


