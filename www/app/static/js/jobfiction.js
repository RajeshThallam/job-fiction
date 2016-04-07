
//GLOBAL VARIABLE
var job_graph = {}
var description_graph = {}

// initialization
$(document).ready(function() {

	// function to set shapeshift plug-in containers
	$('.modelcontainer').shapeshift({
		align:'left',
		minColumns: 3,
		colWidth: 1
	});

	// function to set trash/excluded container in shapeshift
	$(".trash").shapeshift({
		autoHeight: false,
		colWidth: 100,
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

		$.post(
			url = '/home/getkeywords', 
			data = JSON.stringify(job_posts), 
			function(data) {
				console.log(data);

				// remove all existing tokens
				$('.ss-active-child').remove();
				
				for (var key in data) {	
					var keywords = data[key];
					for (var keyword in keywords) {
						addNewToken("#" + key, keyword, key)
						/*if (key === 'must_have') {
							addNewToken("#" + key, keyword, "must_have")
						}
						else if (key === 'nice_have') {
							addNewToken("#" + key, keyword, "nice_have")
						}*/
					}				
				}

				//Graph
				categories = data.categories

				var current_cat = [];  //temp object

		        var cat_counts = []; //counts for level 1 categories//for immediate graph
		        var cat_labels = []; //labels for level 1 categories//for immediate graph
		        var cat1_array = {}; //object for holding all category 1
		         
		        for (var cat in categories){  //cat is the category 1 label                           GENERAL
		            cat_labels.push(cat);//for immediate graph
		            current_cat = categories[cat];
		            var obj_cat1 = {}; //object for holding category 1 information
		            var obj_cat2 = {};  //object for holding category 2 info
		            for (var c_name in current_cat){                                                     //count,  skill, skill
		                  if (c_name == 'count'){
		                    //count is a special category !!
		                    //add count to cat_counts
		                    //add count to object for category 1
		                    cat_counts.push(categories[cat][c_name]); //for immediate graph
		                    obj_cat1["count"] = categories[cat][c_name];
		                  } else{
		                    //put values into some sort of structure that has the category 2 stuff.
		                    //c_name is the category2 name.
		                    obj_cat2[c_name] = categories[cat][c_name];
		                  }
		            }
		            //after loop, add category2 object to cat 2 array
		            obj_cat1["cat2"] = obj_cat2;
		              
		            cat1_array[cat] = obj_cat1;
		        } //end for cat in categories

		        description_graph[0] = cat1_array;   //job_graph is (and MUST) be global

		        createBarChart(cat_labels, cat_counts, "description_graph", "Categories of Skills", 1100, 400, "description_graph");
			}, 
			dataType = 'json'
		);
	});
});

function addNewToken(target, token, type) {
  	var newelement = d3.select(target)
  		.append("div")
		.attr("data-ss-colspan", 2)
		.attr("class", "ss-active-child " + type)
		.attr("id", token);

    newelement.append("p")
		.attr("style","text-align:center")
		.attr("word-wrap", "normal")
		.text(token);

  	$('.modelcontainer').shapeshift({
  		align:'left',
  		minColumns: 3,
  		colWidth: 100
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
	//sendModel();
	//loadResults();

    model_inputs_json = collectModelInputs()
	$.post(
        url = '/home/getresults', 
        data = JSON.stringify(model_inputs_json), 
        function(data) {
            console.log(data);
            loadResults(data);
        },
        dataType = 'json'
    );
}

// this function collects the model and returns it as JSON
function collectModelInputs(){
	var job_title = [];
	var job_desc = [];
	var must_have = [];
	var nice_have = [];
	var exclude = [];

	// loop through all must have
	$("#must_have").find("div").each(function() {
		must_have.push($(this).attr('id'));
	});

	// loop through all nice to have
	$("#nice_have").find("div").each(function() {
		nice_have.push($(this).attr('id'));
	});

	//loop through all exclude
	$("#exclude").find("div").each(function() {
		exclude.push($(this).attr('id'));
	});

    // loop job titles
	$(".user-job-title").each(function() {
		job_title.push($(this).val());
	});

    // loop job descriptions
	$(".user-job-desc").each(function() {
		job_desc.push($(this).val());
	});

    // option - zip code
    if ($("#zip").val().length>0) {
        var zip = $("#zip").val();
    }

    // option - education
    if ($('#education').val() != "None"){
        var education = $('#education').val();
    }

    // option - sort
    if ($('#sort').val() != "None"){
        var sort = $('#sort').val();
    }

	// compose model input JSON
	var strJSON = {
        title: job_title, 
        desc: job_desc, 
        keywords: {
            must_have: must_have, 
            nice_have: nice_have, 
            exclude: exclude
        },
        preferences: {
            zip_code: zip, 
            education: education, 
            sort:sort
        }
    };

    console.log(strJSON);
	return strJSON;
}

//this function loads the results
function loadResults(results){
	//var results = JSON.parse(results_str);

	var parent = document.getElementById("JobResults");
	var table = document.getElementById("tableSearchResults");

	var job_count = 0;
	var job_prefix = "job";
	var current_job;

	//loop through each job:
	for (var job in results){
		job_count++;
		current_job_id = job_prefix + job_count;  //so we can consistently use this.
		current_job = results[job];

		var row = table.insertRow(job_count);
		row.id=current_job_id;
		row.className = "accordion-toggle"; 
		row.setAttribute("data-toggle","collapse");
		row.setAttribute("data-target","#result"+job_count);
		row.setAttribute("data-parent","#JobResults");

		//row information
		var title = row.insertCell(0);
		title.innerHTML = '<strong>' + current_job.job_title + "</strong>";
		var cell = row.insertCell(1);
		cell.innerHTML = current_job.company;
		var cell = row.insertCell(2);
		cell.innerHTML = current_job.location;
		var cell  = row.insertCell(3);
		cell.innerHTML = current_job.job_class[0];
		var cell  = row.insertCell(4);
		cell.innerHTML = current_job.match_rate;
		var cell = row.insertCell(5);
		cell.innerHTML='<i class="indicator glyphicon glyphicon-chevron-up pull-right"></i>';

		//insert hidden row
		row = table.insertRow(job_count+1);
		cell = row.insertCell(0);
		cell.className = "hiddenRow";
		cell.setAttribute("style","padding-bottom:10px;");
		cell.setAttribute("colspan","6");

		//create hidden content
		var section = document.createElement("div");
		section.className = "accordion-body collapse";
		section.id="result"+ job_count;

		//Job Description
		var job_desc = document.createElement("p");
		job_desc.appendChild(document.createTextNode(current_job.job_description));
		section.appendChild(job_desc);

		//Link
		var link = document.createElement("a");
		link.setAttribute("href", current_job.job_url);
		link.appendChild(document.createTextNode("More Information / Apply"));
		section.appendChild(link);
		section.appendChild(document.createElement("br"));

		//*****Info Section******
		var graphicSection = document.createElement("section");
		section.appendChild(graphicSection);
		//-----skill table----
		var skilldiv = document.createElement("div");
		graphicSection.appendChild(skilldiv);
		skilldiv.className = "col-sm-4"
		var skilltable = document.createElement("table");
		skilldiv.appendChild(skilltable);
		skilltable.className = "table table-condensed";
		//skill table rows
		


		skillrow = skilltable.insertRow();
		skillcell = skillrow.insertCell();
		skillcell.innerHTML = "Must Have";
		skillcell = skillrow.insertCell();
		var cellvalue = current_job.skill_match.must_have;
		if (cellvalue < 0){
			cellvalue = 0;
		}
		skillcell.innerHTML = cellvalue;

		skillrow = skilltable.insertRow();
		skillcell = skillrow.insertCell();
		skillcell.innerHTML = "Nice to Have";
		skillcell = skillrow.insertCell();
		var cellvalue = current_job.skill_match.nice_have;
		if (cellvalue < 0){
			cellvalue = 0;
		}
		skillcell.innerHTML = cellvalue;
		//skill table header
		var skillheader = skilltable.createTHead();
		var skillrow = skillheader.insertRow();
		var skillcell = document.createElement("th");
		skillcell.innerHTML = "Skill Category";
		skillrow.appendChild(skillcell);
		skillcell = document.createElement("th");
		skillcell.innerHTML = "Number Matches";
		skillrow.appendChild(skillcell);

		//start of graph part
		var graphdiv = document.createElement("div");
		graphicSection.appendChild(graphdiv);
		graphdiv.id = "skillgraph_" + current_job_id
		graphdiv.className = "col-sm-8"
		
		//take all of this html in section and add it to cell.
		cell.innerHTML=section.outerHTML;
		//doing this now, since the graph part is all SVG stuff.

		//************-----graph----

		
        var categories = current_job.categories;  //get just the categories object

        var current_cat = [];  //temp object

        var cat_counts = []; //counts for level 1 categories//for immediate graph
        var cat_labels = []; //labels for level 1 categories//for immediate graph
        var cat1_array = {}; //object for holding all category 1
         
        for (var cat in categories){  //cat is the category 1 label                           GENERAL
            cat_labels.push(cat);//for immediate graph
            current_cat = current_job.categories[cat];
            var obj_cat1 = {}; //object for holding category 1 information
            var obj_cat2 = {};  //object for holding category 2 info
            for (var c_name in current_cat){                                                     //count,  skill, skill
                  if (c_name == 'count'){
                    //count is a special category !!
                    //add count to cat_counts
                    //add count to object for category 1
                    cat_counts.push(current_job.categories[cat][c_name]); //for immediate graph
                    obj_cat1["count"] = current_job.categories[cat][c_name];
                  } else{
                    //put values into some sort of structure that has the category 2 stuff.
                    //c_name is the category2 name.
                    obj_cat2[c_name] = current_job.categories[cat][c_name];
                  }
            }
            //after loop, add category2 object to cat 2 array
            obj_cat1["cat2"] = obj_cat2;
              
            cat1_array[cat] = obj_cat1;
        } //end for cat in categories

        job_graph[current_job_id] = cat1_array;   //job_graph is (and MUST) be global

        createBarChart(cat_labels, cat_counts, graphdiv.id, "Categories of Skills", 900, 250, current_job_id);

        job_count++; //increment job count
	} // for (var job in results){




}//end loadResults





function createBarChart(labels, values, target_div, title, input_width, input_height, job_id){


  var data = [];
  for (var i = 0; i < labels.length; ++i){
      var obj = {};
      obj.label = labels[i];
      obj.frequency = values[i];
      data.push(obj);
  }

  var margin = {top: 60, right: 20, bottom: 30, left: 40},
      width = input_width - margin.left - margin.right,
      height = input_height - margin.top - margin.bottom;

  var x = d3.scale.ordinal()
      .rangeRoundBands([0, width], .1);

  var y = d3.scale.linear()
      .range([height, 0]);

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom");

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")
      .ticks(10);

  /*var tip = d3.tip()
    .attr('class', 'd3-tip')
    .offset([-5, 0])
    .html(function(d) {
      return "<strong>Frequency:</strong> <span style='color:red'>" + d.frequency + "</span>";
    });
  */
  var svg = d3.select("#"+target_div).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


  //svg.call(tip);

  x.domain(data.map(function(d) { return d.label; }));
  y.domain([0, Math.max(10, d3.max(data, function(d) { return d.frequency; }))]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Frequency");

   var yTextPadding = 20;
	svg.selectAll(".bartext")
	.data(data)
	.enter()
	.append("text")
	.attr("class", "bartext")
	.attr("text-anchor", "middle")
	//.attr("fill", "purple")
	.attr("x", function(d) {return   (Math.min(100,x.rangeBand())/2) + x(d.label) + (x.rangeBand() - d3.min([x.rangeBand(), 100]))/2;})
	.attr("y", function(d) { return y(d.frequency)-5; })
	.text(function(d){return d.frequency;});

  svg.append("text")
        .attr("x", (width / 2))             
        .attr("y", 0 - (margin.top / 2))
        .attr("text-anchor", "middle")  
        .style("font-size", "16px") 
        .style("text-decoration", "underline")  
        .text(title);

  //Graphs will have different on-click functionality depending on target.
  if (target_div == 'modal_drilldown'){
    //no on-click event  -- this is the drill-down chart that has no functionality
    svg.selectAll(".bar")
        .data(data)
      .enter().append("rect")
        .attr("class", "bar")
        .attr("id",job_id)
        .attr("x", function(d) {return  x(d.label) + (x.rangeBand() - d3.min([x.rangeBand(), 100]))/2})
        .attr("width", Math.min(100,x.rangeBand()))
        .attr("y", function(d) { return y(d.frequency); })
        .attr("height", function(d) { return height - y(d.frequency); })
        //.on('mouseover', tip.show)
        //.on('mouseout', tip.hide);
  }else if (target_div == 'modal_graph'){
    //on-click is a drilldown -- this is the graph at top of modal; must have the functionality for drilling down.
    svg.selectAll(".bar")
        .data(data)
      .enter().append("rect")
        .attr("class", "bar")
        .attr("id",job_id)
        .attr("x", function(d) {return  x(d.label) + ((x.rangeBand() - d3.min([x.rangeBand(), 100]))/2);})
        .attr("width", Math.min(100,x.rangeBand()))
        .attr("y", function(d) { return y(d.frequency); })
        .attr("height", function(d) { return height - y(d.frequency); })
        //.on('mouseover', tip.show)
        //.on('mouseout', tip.hide)
        .on('click', function(d){ // show drilldown
            drilldown_chart(d.label, this.id);

        });
  }else{
      //this is just on the main page - click will open modal with chart and drill-down.
      svg.selectAll(".bar")
        .data(data)
      .enter().append("rect")
        .attr("class", "bar")
        .attr("id",job_id)
        .attr("x", function(d) {return  x(d.label) + (x.rangeBand() - d3.min([x.rangeBand(), 100]))/2})
        .attr("width", Math.min(100,x.rangeBand()))
        .attr("y", function(d) { return y(d.frequency); })
        .attr("height", function(d) { return height - y(d.frequency); })
        //.on('mouseover', tip.show)
        //.on('mouseout', tip.hide)
        .on('click', function(d){ //open modal
              openModel(d.label, this.id);
        });

  }


    }

function openModel(source, id){
  //called from graph on a main page - opens modal.
  //source is the label of the category selected
  //id is the job id

  //get the labels and values
    var categories = job_graph[id];
  	if (id == "description_graph"){
  		categories = description_graph[0];
  	}else{
  		categories = job_graph[id];
  	}
    var cat;
    var cat_labels = [];
    var cat_counts = [];

    for (cat in categories){
      cat_labels.push(cat);
      cat_counts.push(categories[cat]["count"]);
    }
    

    document.getElementById("modal_graph").innerHTML = "";
    createBarChart(cat_labels, cat_counts, "modal_graph", "Categories of Skills", 1000, 300, id);
    drilldown_chart(source, id);  //populate the detail
    $('#graphModal').modal('show');  //open the modal
}

function drilldown_chart(source, id){
  //gets the data for the drilldown chart
  //source is the label of the category selected
  //id is the job id

    //get the labels and values
    var topchart;
    if (id == "description_graph"){
    	topchart = description_graph[0];
    }else{
    	topchart = job_graph[id];
    }
    var categories = topchart[source]["cat2"];
    var cat;
    var cat_labels = [];
    var cat_counts = [];

    for (cat in categories){
      cat_labels.push(cat);
      cat_counts.push(categories[cat]);
    }
    document.getElementById("modal_drilldown").innerHTML = "";
    createBarChart(cat_labels, cat_counts, "modal_drilldown", "Count of Skills Related to " + source, 1000, 300, id);
   
}

