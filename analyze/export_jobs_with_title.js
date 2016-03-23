db.jobs.find({}, { _id: 1, jobtitle: 1, company: 1, summary: 1}).forEach( function (x) 
    {     
        var jobdesc = '';
        x.summary.forEach( function (y) { 
            jobdesc += y.replace(/\n/g, ' '); 
        });     
        print(x._id + "!@#" + x.jobtitle + "!@#" + x.company + "!@#" + jobdesc);
    });