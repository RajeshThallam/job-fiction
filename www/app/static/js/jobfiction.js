// initialization
$(document).ready(function() {

	// function to set shapeshift plug-in containers
	$('.modelcontainer').shapeshift({
		align:'left',
		minColumns: 3
	});

	// function to set trash/excluded container in shapeshift
	$(".trash").shapeshift({
		autoHeight: false,
		colWidth: 80,
		enableTrash: true
	});

	// collect user submited job posts and get key words
	$("#btn-collect-job-posts").click(function() {
		var job_title = [];
		var job_desc = [];

		$(".user-job-title").each(function() {
			job_title.push($(this).val());
		});

		$(".user-job-desc").each(function() {
			job_desc.push($(this).val());
		});

		var job_posts = { title: job_title, desc: job_desc};
		console.log(job_posts);

		$.getJSON('/home/getkeywords', data = 'jobposts=' + JSON.stringify(job_posts), function(data) {
			console.log(data);

			// remove all existing tokens
			$('.ss-active-child').remove();
			
			for (var key in data) {	
				var keywords = data[key];
				
				for (var keyword in keywords) {
					if (key == 'must_have') {
						addNewToken("#" + key, keyword, "Auto-Must")
					}
					else {
						addNewToken("#" + key, keyword, "Auto-Nice")
					}
				}
			}
		});

	});
});

function addNewToken(target, token, type) {
  	var newelement = d3.select(target)
  		.append("div")
		.attr("data-ss-colspan", type)
		.attr("class", "ss-active-child")
		.attr("id", token);

    newelement.append("p")
		.attr("style","text-align:center")
		.attr("word-wrap", "normal")
		.text(token);

  	$('.modelcontainer').shapeshift({
  		align:'left',
  		minColumns: 3
  	});
};

function setOptions(){
	var educationOpt = document.getElementById('education').value;
	var sortOpt = document.getElementById('sort').value;
	var compInfoOpt = document.getElementById('IncComp').value;
	var visualOpt = document.getElementById('IncVisual').value;

	var optionString = "";
	if (educationOpt != 'None') {
		optionString = optionString + "Education: " + educationOpt;
	}

	optionString = optionString + "Sort by: " + sortOpt;
	optionString = optionString + "Company Info: " + compInfoOpt;
	optionString = optionString + "Visual Include: " + visualOpt;

	document.getElementById('savedOptions').innerHTML = optionString;
}
