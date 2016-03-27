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

	var optionString = "";
	optionString = optionString + "<strong>Sort by:</strong> " + sortOpt;
		if (educationOpt != 'None') {
			optionString = optionString + "; <strong>Education: </strong> " + educationOpt;
	}

	optionString = optionString + "Sort by: " + sortOpt;

	document.getElementById('savedOptions').innerHTML = optionString;
}

	//this function just coordinates the retrieval of the job lists.
	function getResults(){
		alert("get results");
		sendModel();
		loadResults();
	}

	//this function sends the model
	function sendModel(){
		alert("sendModel");
		var model_json = collectModel();

		//do stuff here to send the model
	}

	//this function collects the model and returns it as JSON
	function collectModel(){


		var must_have = [];
		var nice_to_have = [];
		var exclude = [];

		//loop through all must have
		var ancestor = document.getElementById('must_have'), 
			decendents = ancestor.getElementsByTagName('div');
		var i, element, token;

		for (i = 0; i < decendents.length; i++){
			element = decendents[i];
			token = element.id;
			if (token != 'Placeholder_temp'){
				must_have.push(token);	
			}
			

		}

		//loop through all must have
		var ancestor = document.getElementById('nice_to_have'), 
			decendents = ancestor.getElementsByTagName('div');
		var i, element, token;
		for (i = 0; i < decendents.length; i++){
			element = decendents[i];
			token = element.id;
			if (token != 'Placeholder_temp'){
				nice_to_have.push(token);	
			}
			

		}
		//loop through all exclude
		var ancestor = document.getElementById('exclude'), 
			decendents = ancestor.getElementsByTagName('div');
		var i, element, token;
		for (i = 0; i < decendents.length; i++){
			element = decendents[i];
			token = element.id;
			if (token != 'Placeholder_temp'){
				exclude.push(token);	
			}			

		}

		//compose JSON
		//NOTE - yes, creation of each tmpSTR could have been done above, but at this time it is not
		//certain how it is best to create JSON, so this gives most flexibility
		var strJSON = "";

		//must_have
		var tmpSTR = ""
		for (var i=0; i < must_have.length; i++){
			if (tmpSTR.length > 0){
				tmpSTR = tmpSTR + ', "' + must_have[i] + '":0';
			}else{ //first one does not start with comma
				tmpSTR = tmpSTR + '"' + must_have[i] + '":0';
			}

		}
		if (tmpSTR.length > 0){
			if (strJSON.length > 0){
				strJSON = strJSON + ', "must_have":{' + tmpSTR + '}';	
			}else{
				strJSON = strJSON + '"must_have":{' + tmpSTR + '}';	
			}
		}

		//nice_to_have
		var tmpSTR = ""
		for (var i=0; i < nice_to_have.length; i++){
			if (tmpSTR.length > 0){
				tmpSTR = tmpSTR + ', "' + nice_to_have[i] + '":0';
			}else{ //first one does not start with comma
				tmpSTR = tmpSTR + '"' + nice_to_have[i] + '":0';
			}

		}
		if (tmpSTR.length > 0){
			if (strJSON.length > 0){
				strJSON = strJSON + ', "nice_to_have":{' + tmpSTR + '}';	
			}else{
				strJSON = strJSON + '"nice_to_have":{' + tmpSTR + '}';	
			}
		}		

		//exclude
		var tmpSTR = ""
		for (var i=0; i < exclude.length; i++){
			if (tmpSTR.length > 0){
				tmpSTR = tmpSTR + ', "' + exclude[i] + '":0';
			}else{ //first one does not start with comma
				tmpSTR = tmpSTR + '"' + exclude[i] + '":0';
			}

		}
		if (tmpSTR.length > 0){
			if (strJSON.length > 0){
				strJSON = strJSON + ', "exclude":{' + tmpSTR + '}';	
			}else{
				strJSON = strJSON + '"exclude":{' + tmpSTR + '}';	
			}
		}	

		//option - zip code
		e = document.getElementById('zip')
		if (e.value.length>0){
			if (strJSON.length>0){
				strJSON = strJSON + ', "zip":"' + e.value + '"';
			}else{
				strJSON = strJSON + '"zip":"' + e.value + '"';
			}			
		}

		//option - education
		e = document.getElementById('education')
		value = e.options[e.selectedIndex].value
		if (value != "None"){
			if (strJSON.length>0){
				strJSON = strJSON + ', "education": "' + value + '"';
			}else{
				strJSON = strJSON + '"education": "' + value + '"';
			}			
		}		

		//option - sort
		e = document.getElementById('sort')
		value = e.options[e.selectedIndex].value
		if (e.value != "None"){
			if (strJSON.length>0){
				strJSON = strJSON + ', "sort": "' + value + '"';
			}else{
				strJSON = strJSON + '"sort": "' + value + '"';
			}			
		}	

		//final closure
		if (strJSON.length > 0){
			strJSON = "{" + strJSON + "}";
		}

		alert (strJSON);
		return strJSON;

	}

	//this function loads the results
	function loadResults(){
		alert("loadResults");
	}
