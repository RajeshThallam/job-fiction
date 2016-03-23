High level contract/interface definitions

- Job Descriptions Page to MAUI Keyword Extractor
     Input to MAUI
     - 3 job descriptions as an array of text string

- MAUI Keyword Extractor to Model page
     -  {
            must_have: {skill: score},
            nice_to_have: {skill: score},
            may_be: {skill: score}
        }

- Model Page to Recommender
     - {
            job_descriptions: [],
            job_titles: []
            keywords: { must_have: [], nice_to_have: [], may_be: [] },
            preferences: {
                zip_code: number,
                radius: number #(or we can default within 50 miles),
                industry: [],
                companies: []
            },
        }  

- Recommender to Results Page
      - {
            job_title: string,
            job_description: string #may have formatting issue,
            job_url: url,
            company: string,
            industry: string,
            job_class: string
            match_rate: string,
            location: string, #city, state, zip
            skill_match: { must_have: [ {skill: pct} ], nice_to_have: [ {skill: pct} ], may_be: [ {skill: pct} ] }
​         }​