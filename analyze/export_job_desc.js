db.jobs.find( { "jobtitle" : /driver/i }, { _id: 1, summary: 1}).limit(1).forEach( function (x) 
	{     
		var jobdesc = '';
		x.summary.forEach( function (y) { 
			jobdesc += y.replace('\n', ' ').replace('\n', ' '); 
		});     
		print(x._id + "!@#" +jobdesc.replace('\n', ' ')); 
	});

`mongo JOBFICTION --quiet export_job_desc.js > export.txt