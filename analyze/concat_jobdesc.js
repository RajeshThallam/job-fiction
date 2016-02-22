db.jobs.find({_id: 'indeed_2248d91cabe9f4c1'}, { _id: 0, summary: 1}).forEach( function (x) {
    var jobdesc = '';
    
    x.summary.forEach( function (y) { jobdesc += y; })
    print jobdesc;
});