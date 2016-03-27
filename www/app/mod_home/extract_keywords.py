#!/usr/bin/python

import json
import sys

# read job descriptions as string
job_posts = sys.argv[1]

# replace with MAUI extract
keywords = {
        "must_have": {
            "Python": 0,
            "D3": 0,
            "Analytics": 0,
            "Data Modeling": 0,
            "Software Development": 0,
            "Visualization": 0
        },
        "nice_to_have": {
            "Database": 0,
            "Research": 0,
            "Design": 0,
            "Oracle": 0,
            "Data Management": 0,
            "Competitive": 0,
            "Leadership": 0,
            "Data Collection": 0
        }
    }

print json.dumps(keywords)