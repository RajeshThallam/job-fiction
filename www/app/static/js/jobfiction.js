
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

    // add sorter plug-in
    $('#tableSearchResults').tablesorter({ 
        widthFixed: false
    });

	// add search on the results table
	$(".search").on("keyup change", function () {
		var searchTerm = $(".search").val();
		var listItem = $('.results tbody').children('tr');
		var searchSplit = searchTerm.replace(/ /g, "'):containsi('")
    
		if(searchTerm == ""){
			$(".results tbody tr").each(function(e){
				$(this).attr('visible','true'); 
			});
			$('.counter').text('');
			return 0;
		}

		$.extend($.expr[':'], {'containsi': function(elem, i, match, array){
			return (elem.textContent || elem.innerText || '').
				toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;}
  		});
    
		$(".results tbody tr").not(":containsi('" + searchSplit + "')").each(
			function(e){
			$(this).attr('visible','false');
		});

		$(".results tbody tr:containsi('" + searchSplit + "')").each(
			function(e){
			$(this).attr('visible','true');
			$(this).next('tr').attr('visible','true');
		});

		var jobCount = $('.results tbody tr[visible="true"]').length;
		$('.counter').text(jobCount/2 + (jobCount/2 <= 1 ? ' job': ' jobs'));

		if(jobCount == '0') {$('.no-result').show();}
		else {$('.no-result').hide();}
	});

	// collect user submited job posts and get key words
	$("#btn-collect-job-posts").click(function() {
        if ($("#resultsprogressbar").css("display") == "block" ||
            $("#modelprogressbar").css("display") == "block" ) {
            return 1;
        }
        
        $('#tableSearchResults_body').find("tr:gt(0)").remove();
        $('#tableSearchResults_body').find("tr:eq(0)").hide();

		$("#description_graph").css("display", "none");
		var bar = "";
		bar = new ProgressBar.Line('#modelprogressbar', {
		  strokeWidth: 4,
		  easing: 'easeInOut',
		  duration: 20000,
		  color: '#337AB7',
		  trailColor: '#eee',
		  trailWidth: 1,
		  svgStyle: {width: '100%', height: '100%'},
		  text: {
		    style: {
		      color: '#337AB7',
		      position: 'absolute',
		      right: '0',
		      top: '30px',
		      padding: 0,
		      margin: 0,
		      transform: null,
		      fontFamily: '"Raleway", Helvetica, sans-serif',
		      fontSize: '1.5rem'
		    },
		    autoStyleContainer: false
		  },
		  from: {color: '#337AB7'},
		  to: {color: '#ED6A5A'},
		  step: function(state, bar) {
		    bar.setText('Analyzing... ' + Math.round(bar.value() * 100) + ' %');
		  }
		});

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

		$("#modelprogressbar").css("display", "block");
		bar.animate(1.0);  // Number from 0.0 to 1.0

		$.post(
			url = '/home/getkeywords', 
			data = JSON.stringify(job_posts), 
			function(data) {
				console.log(data);
				bar.destroy();
				$("#modelprogressbar").css("display", "none");
                $('#tableSearchResults_body').find("tr:gt(0)").remove();
                $('#tableSearchResults_body').find("tr:eq(0)").hide();

				// remove all existing tokens
				$('.ss-active-child').remove();
				
				for (var key in data) {	
					var keywords = data[key];
					for (var keyword in keywords) {
						addNewToken("#" + key, keyword, key)
					}				
				}

				//Graph
				categories = data.categories

				var current_cat = [];  //temp object
		        var cat_counts = []; //counts for level 1 categories//for immediate graph
		        var cat_labels = []; //labels for level 1 categories//for immediate graph
		        var cat1_array = {}; //object for holding all category 1
		         
		        for (var cat in categories){  //cat is the category 1 label
		            cat_labels.push(cat);//for immediate graph
		            current_cat = categories[cat];
		            var obj_cat1 = {}; //object for holding category 1 information
		            var obj_cat2 = {};  //object for holding category 2 info
		            for (var c_name in current_cat){
		            	//count,  skill, skill
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
				
				document.getElementById("description_graph").innerHTML = "";
				$("#description_graph").css("display", "block");
		        //createBarChart(cat_labels, cat_counts, "description_graph", "Categories of Skills", 1100, 500, "description_graph");
		        horizontal_graph(cat_labels, cat_counts, "description_graph", "Categories of Skills", 1000, 400, "description_graph");
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
		.attr("style","text-align:center; color: black;")
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
    if ($("#resultsprogressbar").css("display") == "block" ||
        $("#modelprogressbar").css("display") == "block" ) {
        return 1;
    }

    $("#JobResults").css("display", "none");
    var bar = "";
    bar = new ProgressBar.Line('#resultsprogressbar', {
      strokeWidth: 4,
      easing: 'easeInOut',
      duration: 5000,
      color: '#337AB7',
      trailColor: '#eee',
      trailWidth: 1,
      svgStyle: {width: '100%', height: '100%'},
      text: {
        style: {
          color: '#337AB7',
          position: 'absolute',
          right: '0',
          top: '30px',
          padding: 0,
          margin: 0,
          transform: null,
          fontFamily: '"Raleway", Helvetica, sans-serif',
          fontSize: '1.5rem'
        },
        autoStyleContainer: false
      },
      from: {color: '#337AB7'},
      to: {color: '#ED6A5A'},
      step: function(state, bar) {
        bar.setText('Searching the best... ' + Math.round(bar.value() * 100) + ' %');
      }
    });

    $("#resultsprogressbar").css("display", "block");
    bar.animate(1.0);  // Number from 0.0 to 1.0

    model_inputs_json = collectModelInputs()
	$.post(
        url = '/home/getresults', 
        data = JSON.stringify(model_inputs_json), 
        function(data) {
            console.log(data);
            getResultsES(data, bar);
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

function getResultsES(match_jobs, bar){
	var scores = {}
	match_jobs['jobs'].map(function(job) { scores[job[0]] = parseFloat(job[1]); });

	var job_ids = Object.keys(scores);
	//job_ids = [ "indeed_4da5859d10426dab", "indeed_8e1f2f2909654316" ]

	// prepare ES query call
	var s_ES = "http://50.97.254.20:9200";
	var es_call = '{"size":' + job_ids.length + 
		', "query": {"filtered" : {"filter" : {"terms": {"_id":["' + 
		job_ids.join('", "') + 
		'"]}}}}}'
	//console.log(es_call)

	// REST API to query ES and get results
	$.post(
        url = s_ES + '/jobfiction/results/_search?pretty=true',
        data = es_call,
        function(data) {
        	// get results from ElasticSearch Server
            console.log(data);
            results = data.hits.hits
            console.log("# of results retreived " + results.length)

            // reorder results from ES based on relevance as 
            // returned by the model 
			srt_results = []
			job_ids.forEach(function(key) {
			    var found = false;
			    items = results.filter(function(item) {
			        if(!found && item._id == key) {
			            srt_results.push(item);
			            found = true;
			            return false;
			        } else 
			            return true;
			    })
			});

			// call function to display results
            loadResults(srt_results, scores, bar);
        },
        dataType = 'json'
    );


}

//this function loads the results
function loadResults(results, match_rates, statusBar){
	//var results = JSON.parse(results_str);
	var parent = document.getElementById("JobResults");
	var table = document.getElementById("tableSearchResults");

	// var tb = document.getElementById('tableSearchResults_body');
	// tb.innerHTML="";
    $('#tableSearchResults_body').find("tr:gt(0)").remove();
	
	var tb = document.getElementById('tableSearchResults').getElementsByTagName('tbody')[0];
	var job_count = 0;
	var job_prefix = "job";
	var current_job;
    var user_pref_match_score = 0.0;

	var user_must_have = [];
    var user_nice_have = [];
    var user_exclude = [];
    var must_have = [];
    var nice_have = [];
    var exclude = [];    

	// loop through all must have
	$("#must_have").find("div").each(function() {
		user_must_have.push($(this).attr('id'));
	});

	// loop through all nice to have
	$("#nice_have").find("div").each(function() {
		user_nice_have.push($(this).attr('id'));
	});
    
	// loop through all exclude
	$("#exclude").find("div").each(function() {
		user_exclude.push($(this).attr('id'));
	});
    
    var total_pref = 
        user_must_have.length +
        user_nice_have.length +
        user_exclude.length;

	//loop through each job:
	for (var job in results){
		if (job < results.length) {
			var current_idx = job_count++;
			current_job_id = job_prefix + current_idx;  //so we can consistently use this.
			current_job = results[job]._source;
			job_id = results[job]._id;

			var row = tb.insertRow(current_idx);
			row.id=current_job_id;
			row.className = "accordion-toggle"; 
			row.setAttribute("data-toggle","collapse");
			row.setAttribute("data-target","#result"+job_count);
			row.setAttribute("data-parent","#JobResults");

            // derive skill preference match score
			results_skills = Object.keys(current_job.keywords.must_have)
					.concat(Object.keys(current_job.keywords.nice_have));

            must_have = results_skills.filter(function(n) {
                return user_must_have.indexOf(n) != -1;
            });

            nice_have = results_skills.filter(function(n) {
                return user_nice_have.indexOf(n) != -1;
            });
            
            exclude = results_skills.filter(function(n) {
                return user_exclude.indexOf(n) != -1;
            });

			//row information
			var title = row.insertCell(0);
            title.style.width = '380px';
			title.innerHTML = '<strong>' + current_job.job_title + '</strong>';
			var cell = row.insertCell(1);
            cell.style.width = '380px';
			cell.innerHTML = current_job.company;
			var cell = row.insertCell(2);
            cell.style.width = '190px';
			cell.innerHTML = current_job.full_location.replace(/\d+$/g, '');
			var cell  = row.insertCell(3);
            cell.style.width = '190px';
			cell.innerHTML = current_job.job_class[0]['label'];
			var cell  = row.insertCell(4);
            cell.style.width = '100px';
			// cell.innerHTML = (	current_job.job_class[0]['score']*100).toFixed(2);
            user_pref_match_score = ((must_have.length * 2) + (nice_have.length * 1) + (exclude.length * -2)); 
            cell.innerHTML = user_pref_match_score;
			var cell = row.insertCell(5);
            cell.style.width = '100px';
			cell.innerHTML = ((match_rates[job_id] + user_pref_match_score*.01)*100).toFixed(2);
			var cell = row.insertCell(6);
			cell.innerHTML='<i class="indicator glyphicon glyphicon-chevron-up pull-right"></i>';

			//insert hidden row
			row = table.insertRow(job_count+1);
			row.className = "expand-child"
			cell = row.insertCell(0);
			cell.className = "hiddenRow ";
			cell.setAttribute("style","padding-bottom:10px;");
			cell.setAttribute("colspan","6");

			//create hidden content
			var section = document.createElement("div");
			section.className = "accordion-body collapse";
			section.id="result"+ job_count;

			//Job Description
			//var job_desc = document.createElement("p");
			//job_desc.appendChild(document.createTextNode(current_job.job_description));
			//section.appendChild(job_desc);

			//Link
			var link = document.createElement("a");
			link.setAttribute("href", current_job.url);
			link.setAttribute("target","_blank");
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

			if ( 'keywords' in current_job) {
				skillrow = skilltable.insertRow();
				skillcell = skillrow.insertCell();
				skillcell.innerHTML = "Must Have";
				skillcell = skillrow.insertCell();
				var cellvalue = must_have.length;
				if (cellvalue < 0){
					cellvalue = 0;
				}
				skillcell.innerHTML = cellvalue;

				skillrow = skilltable.insertRow();
				skillcell = skillrow.insertCell();
				skillcell.innerHTML = "Nice to Have";
				skillcell = skillrow.insertCell();
				var cellvalue = nice_have.length;
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
			}

			//start of graph part
			var graphdiv = document.createElement("div");
			graphicSection.appendChild(graphdiv);
			graphdiv.id = "skillgraph_" + current_job_id
			graphdiv.className = "col-sm-8"
			
			//take all of this html in section and add it to cell.
			cell.innerHTML=section.outerHTML;
			//doing this now, since the graph part is all SVG stuff.

			//************-----graph----
			
			if ( 'keywords' in current_job) {
		        var categories = current_job.keywords.categories;  //get just the categories object

		        var current_cat = [];  //temp object

		        var cat_counts = []; //counts for level 1 categories//for immediate graph
		        var cat_labels = []; //labels for level 1 categories//for immediate graph
		        var cat1_array = {}; //object for holding all category 1
		         
		        for (var cat in categories){  //cat is the category 1 label                           GENERAL
		            cat_labels.push(cat);//for immediate graph
		            current_cat = current_job.keywords.categories[cat];
		            var obj_cat1 = {}; //object for holding category 1 information
		            var obj_cat2 = {};  //object for holding category 2 info
		            for (var c_name in current_cat){                                                     //count,  skill, skill
		                  if (c_name == 'count'){
		                    //count is a special category !!
		                    //add count to cat_counts
		                    //add count to object for category 1
		                    cat_counts.push(current_job.keywords.categories[cat][c_name]); //for immediate graph
		                    obj_cat1["count"] = current_job.keywords.categories[cat][c_name];
		                  } else{
		                    //put values into some sort of structure that has the category 2 stuff.
		                    //c_name is the category2 name.
		                    obj_cat2[c_name] = current_job.keywords.categories[cat][c_name];
		                  }
		            }
		            //after loop, add category2 object to cat 2 array
		            obj_cat1["cat2"] = obj_cat2;
		              
		            cat1_array[cat] = obj_cat1;
		        } //end for cat in categories

		        job_graph[current_job_id] = cat1_array;   //job_graph is (and MUST) be global

		        horizontal_graph(cat_labels, cat_counts, graphdiv.id, "Categories of Skills", 900, 250, current_job_id);
		    }
		}
        job_count++; //increment job count
	} // for (var job in results){

	$("#tableSearchResults").trigger("update");
    var sorting = [[5,1]]; 
    $("#tableSearchResults").trigger("sorton",[sorting]);
    $("#tableSearchResults").trigger("update"); 

    //bar = ProgressBar('#resultsprogressbar');
    statusBar.destroy();
    $("#resultsprogressbar").css("display", "none");
    $("#JobResults").css("display", "block");

}//end loadResults

function createBarChart(labels, values, target_div, title, input_width, input_height, job_id){

  document.getElementById(target_div).innerHTML = "";

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
    //createBarChart(cat_labels, cat_counts, "modal_graph", "Categories of Skills", 1000, 300, id);
    horizontal_graph(cat_labels, cat_counts, "modal_graph", "Categories of Skills", 800, 300, id);
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
    //createBarChart(cat_labels, cat_counts, "modal_drilldown", "Count of Skills Related to " + source, 1000, 300, id);
  	horizontal_graph(cat_labels, cat_counts, "modal_drilldown", "Count of Skills Related to " + source, 800, 300, id);
}


function horizontal_graph(labels, values, target_div, title, input_width, input_height, job_id){
	Array.prototype.max = function() {
      return Math.max.apply(null, this);
    };

  	Array.prototype.longest=function() {
  		return this.sort(
  			function(a,b) {  
  				if (a.length > b.length) return -1;
  				if (a.length < b.length) return 1;
  				return 0
  			}
  			)[0];
  	}

    // sort labels alphabetically and respective values
    orig_labels = labels.slice();
    srt_labels = labels.sort();
    srt_values = srt_labels.map(function(label) { 
        return values[orig_labels.indexOf(label)];
    });

    labels = srt_labels;
    values = srt_values;

    var tmp_labels = labels.slice();
    var maxLabel = tmp_labels.sort(function (a, b) { return b.length - a.length })[0];
    var maxLabelLength = 45;//maxLabel.length;
    var maxValue = [values.max()+5,10].max() +2;
    var colors = ['#0000b4','#0082ca','#0094ff','#0d4bcf','#0066AE','#074285','#00187B','#285964','#405F83','#416545','#4D7069','#6E9985','#7EBC89','#0283AF','#79BCBF','#99C19E'];

    var margin = {top: 40, right: 20, bottom: 30, left: 40},
        width = input_width - margin.left - margin.right,
        height = input_height - margin.top - margin.bottom;

    //var width = width;  //target size of div
    //var height = height;  //target height of div
    var transform_x = maxLabelLength*8; //moves whole chart left or right (distance from edge)

    var y2 = height -20; //actual height of chart (controls where x axis is)
    var x2 = width - transform_x; //actual width of chart (controls where y axis is)

    var y_xis_transform_y = margin.top;  //adjustment of chart content up and down

    var yscale_range_y = height - margin.top - margin.bottom +10; //spread of y axis.
    var bar_height = 15;  //width of bars (height because it is vertical size of rect)

    var space = x2/(maxValue);  //space between grid lines.

    var grid = d3.range(maxValue).map(function(i){
      return {'x1':0,'y1':margin.top,'x2':0,'y2':y2};
    });

    var tickVals = grid.map(function(d,i){
      if(i>0){ return i; }
      else if(i===0){ return "100";}
    });
    //domain is tick range
    var xscale = d3.scale.linear()
            .domain([0,maxValue])
            .range([0,x2]);

    var yscale = d3.scale.linear()
            .domain([0,labels.length])
            .range([0,yscale_range_y]);

    var colorScale = d3.scale.quantize()
            .domain([0,labels.length])
            .range(colors);

    var categoryColorScale = d3.scale.category20b()
            .domain([
                "Analytical or Scientific Analysis",
                "Applied computing",
                "BI/Data Visualization",
                "Computer Infrastructure",
                "Data and Information Management",
                "Data Models",
                "Data Visualization",
                "Development Software",
                "Development Technologies",
                "Distributed Computing",
                "ERP Software",
                "Hardware",
                "Human-centered computing",
                "Internet of Things",
                "Machine Learning",
                "Math and Statistics",
                "Quality Assurance",
                "Security and privacy",
                "Theory of computation",
                "Dummy"
            ]);

    var canvas = d3.select('#'+target_div)
            .append('svg')
            .attr({'width':width,'height':height})
            .attr('id',target_div);


    
    //grid lines
    var grids = canvas.append('g')
              .attr('id','grid')
              .attr('transform','translate('+transform_x+',0)')
              .selectAll('line')
              .data(grid)
              .enter()
              .append('line')
              .attr({'x1':function(d,i){ return i*space; },
                 'y1':function(d){ return d.y1; },
                 'x2':function(d,i){ return i*space; },
                 'y2':function(d){ return d.y2; },
              })
              .style({'stroke':'#adadad','stroke-width':'0px'});

    //y axis line and labels  
    var yAxis = d3.svg.axis();
      yAxis
        .orient('left')
        .scale(yscale)
        .tickSize(2)
        .tickFormat(function(d,i){ return labels[i]; })
        .tickValues(d3.range(30));

    var y_xis = canvas.append('g')
              .attr("transform", "translate("+transform_x+", " + y_xis_transform_y+ ")")
              .attr('id','yaxis')
              .call(yAxis);

	y_xis.selectAll("text")
      .attr('y', 6);              

    //x axis line and labels
    var xAxis = d3.svg.axis();
      xAxis
        .orient('bottom')
        .scale(xscale)
        .tickValues(tickVals);

    var x_xis = canvas.append('g')
              .attr("transform", "translate("+transform_x+"," + y2 + ")")
              .attr('id','xaxis')
              .call(xAxis);

    var title = canvas.append("text")
        .attr("x", ((width / 2) + (transform_x/2)))
        .attr("y", 30)//0 - (margin.top / 2))
        .attr("text-anchor", "middle")  
        .style("font-size", "16px") 
        .style("text-decoration", "underline")  
        .text(title);

  //Graphs will have different on-click functionality depending on target.
  if (target_div == 'modal_drilldown'){
    //no on-click event  -- this is the drill-down chart that has no functionality
    var chart = canvas.append('g')
              .attr("transform", "translate("+transform_x+",0)")
              .attr('id','bars')
              .selectAll('rect')
              .data(values)
              .enter()
              .append('rect')
              .attr('height',bar_height)
              .attr('id',function(d,i){return labels[i] +'|'+ job_id;})
              .attr({'x':0,'y':function(d,i){ return yscale(i)+y_xis_transform_y; }})
              .style('fill',function(d,i){ return colorScale(i); })
              .attr('width',function(d){ return d*space; });
        //.on('mouseover', tip.show)
        //.on('mouseout', tip.hide);
  }else if (target_div == 'modal_graph'){
    //on-click is a drilldown -- this is the graph at top of modal; must have the functionality for drilling down.
    var chart = canvas.append('g')
              .attr("transform", "translate("+transform_x+",0)")
              .attr('id','bars')
              .selectAll('rect')
              .data(values)
              .enter()
              .append('rect')
              .attr('height',bar_height)
              .attr('id',function(d,i){return labels[i] +'|'+ job_id;})
              .attr({'x':0,'y':function(d,i){ return yscale(i)+y_xis_transform_y; }})
              .style('fill',function(d,i){ return categoryColorScale(labels[i]); })
              .attr('width',function(d){return d * space; })
              .on('click', function(d){ //update drilldown
              					var tokens = this.id.split("|");
              					drilldown_chart(tokens[0], tokens[1]);

        			});
        
  }else{
      //this is just on the main page - click will open modal with chart and drill-down.
      var chart = canvas.append('g')
              .attr("transform", "translate("+transform_x+",0)")
              .attr('id','bars')
              .selectAll('rect')
              .data(values)
              .enter()
              .append('rect')
              .attr('height',bar_height)
              .attr('id',function(d,i){return labels[i] +'|'+ job_id;})
              .attr({'x':0,'y':function(d,i){ return yscale(i)+y_xis_transform_y; }})
              .style('fill',function(d,i){ return categoryColorScale(labels[i]); })
              .attr('width',function(d){ return d * space; })
              .on('click', function(d){ //open modal
              					var tokens = this.id.split("|");
              					openModel(tokens[0], tokens[1]);
        			});

  }


    //draws the bars
    var transit = d3.select(target_div).selectAll("rect")
                .data(values)
                .transition()
                .duration(1000) 

                .attr("width", function(d) {return xscale(d); });


/*
    //white text
    var transitext = d3.select('#bars')
              .selectAll('text')
              .data(values)
              .enter()
              .append('text')

              .attr({'x':function(d) {return xscale(d)-20; },'y':function(d,i){ return yscale(i) + margin.top + 12; }})
              .text(function(d){ return d; }).style({'fill':'white'});
*/


}//end function horizontal_graph 
