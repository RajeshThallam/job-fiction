import json

class ModelTalking(object): 
    def get_job_recommendations(self, model_inputs_json):
        job_results = {
            "result_1": {
               "job_title": "Data Scientist",
               "job_description": "Job description As a Data Science Consultant at RBA, you will work on client projects in ",
               "job_url": "http: //careers.intuit.com/job-category/7/data/job/00122116/data-scientist?src=JB-10116&utm_source=indeed&utm_medium=jb",
               "company": "Intuit",
               "industry": "Finance",
               "job_class": ["Data Scientist"],
               "match_rate": 52,
               "location": "Mountain View, California 94039",
               "skill_match": {
                  "must_have": 5,
                  "nice_to_have": 3
               },
               "categories": {
                  "GENERAL": {
                     "count": 3,
                     "Integrated Circits": 1,
                     "Real-time systems": 2
                  },
                  "MATHEMATICS": {
                     "count": 1,
                     "Mathematical Software": 1
                  },
                  "COMPUTING": {
                     "count": 8,
                     "Machine learning": 5,
                     "Modeling and simulation": 2,
                     "Electronic commerce": 1
                  },
                  "HUMAN": {
                     "count": 2,
                     "Visualization": 2
                  },
                  "PROFESSIONAL": {
                     "count": 2,
                     "Computing Technology policy": 2
                  }
               }
            },
            "result_2": {
               "job_title": "Analyst",
               "job_description": "iashjdf kasdfoaksdfv  l;askdjf; asdx kajsdf kal;skdx laskd sdakas dfksadl;kfmk;asdc ;sadfkncl;kdsf ",
               "job_url": "http: //careers.intuit.com/job-category/7/data/job/00122116/data-scientist?src=JB-10116&utm_source=indeed&utm_medium=jb",
               "company": "Place To Work",
               "industry": "Finance",
               "job_class": ["Data Scientist"],
               "match_rate": 52,
               "location": "Mountain View, California 94039",
               "skill_match": {
                  "must_have": 1,
                  "nice_to_have": 1
               },
               "categories": {
                  "GENERAL": {
                     "count": 1,
                     "Integrated Circits": 1
                  },
                  "MATHEMATICS": {
                     "count": 1,
                     "Mathematical Software": 1
                  },
                  "COMPUTING": {
                     "count": 14,
                     "Machine learning": 7,
                     "Modeling and simulation": 2,
                     "Electronic commerce": 5
                  },
                  "HUMAN": {
                     "count": 2,
                     "Visualization": 2
                  },
                  "PROFESSIONAL": {
                     "count": 4,
                     "Computing Technology policy": 2,
                     "presentations": 2
                  }
               }
            }
        }

        return json.dumps(job_results)