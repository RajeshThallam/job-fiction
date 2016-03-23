db.jobs.aggregate([
	{$group : {_id : {company: "$company"},count: { $sum: 1 } } }, 
	{$sort  : { count: -1 } }, 
	{$limit : 20} 
]);