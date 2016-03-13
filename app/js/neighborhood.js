// Base Elastic Search URL
//url_business_base = "http://54.183.182.71:9200/yelp/business/_search?size=2000"

function print_filter(filter){
    var f=eval(filter);
    if (typeof(f.length) != "undefined") {}else{}
    if (typeof(f.top) != "undefined") {f=f.top(Infinity);}else{}
    if (typeof(f.dimension) != "undefined") {f=f.dimension(function(d) { return "";}).top(Infinity);}else{}
    console.log(filter+"("+f.length+") = "+JSON.stringify(f).replace("[","[\n\t").replace(/}\,/g,"},\n\t").replace("]","\n]"));
}

//Width and height
var w = 1400;
var h = 200;
var barPadding = 0.2;
var margin = {top:100,bottom:100,right:100,left:100};

//Custom Icon
var neighborsIcon = L.icon({
    iconUrl: 'img/fork55.png',
    //shadowUrl: 'leaf-shadow.png',

    iconSize:     [25, 40], // size of the icon
    //shadowSize:   [50, 64], // size of the shadow
    iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
    //shadowAnchor: [4, 62],  // the same for the shadow
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});

var myIcon = L.icon({
    iconUrl: 'img/myrest.png',
    //shadowUrl: 'leaf-shadow.png',

    iconSize:     [40, 75], // size of the icon
    iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});


/* Get the lat/lon */
//url_1 = '{"query":{"match":{"business_id":"4bEjOyTaDG24SY5TxsaUNQ"}},"fields":["longitude","latitude","categories"]}'


var lat = null;
var lon = null;
var url_2 = null;

d3.json('./json/business_4bEjOyTaDG24SY5TxsaUNQ.json', function(error, d){
    if (error) {  //If error is not null, something went wrong.
        console.log(error);  //Log the error.
    } else {      //If no error, the file loaded correctly. Yay!
        console.log(d);
    }

    lat = d.hits.hits[0].fields.latitude[0]
    lon = d.hits.hits[0].fields.longitude[0]
    console.log(lon + ',' + lat);

    var categories = d.hits.hits[0].fields.categories.join(' ')
    console.log(categories);


    /* Get neighborhood businesses */

    //url_2 = '{"query":{"filtered":{"query":{"match":{"categories":{"query":"' + categories + '","minimum_should_match":1}}},"filter":{"geo_distance":{"distance":"1km","location":{"lat":' + lat + ',"lon":' + lon + '}}}}},"fields":["name","longitude","latitude","categories","stars","review_count"]}'
    //console.log(url_2);

    d3.json('./json/neighborhood.json', function(error, d){
        if (error) {  //If error is not null, something went wrong.
            console.log(error);  //Log the error.
        } else {      //If no error, the file loaded correctly. Yay!
            console.log('Total # Business in Neighborhood: ' + d.hits.total);
        }

        //Draw the Map
        var map = L.map('map').setView([lat, lon], 15);
        var circle = L.circle([lat,lon], 250, {
            color: 'red',
            fillColor: '#f03',
            fillOpacity: 0.5
        }).addTo(map);

        // load a tile layer
        L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoidGFsazJzYXlhbnRhbiIsImEiOiJjaWhyN29oeHUwMDRjdHNraGt2c2tnMGV0In0.UUa_E3pP4tUvc8JClZ2yBg', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
            maxZoom: 18,
            id: 'talk2sayantan.ob6ndhba',
            accessToken: 'pk.eyJ1IjoidGFsazJzYXlhbnRhbiIsImEiOiJjaWhyN29oeHUwMDRjdHNraGt2c2tnMGV0In0.UUa_E3pP4tUvc8JClZ2yBg'
        }).addTo(map);

        neighborhood = []

        for(i in d.hits.hits) {
            data = d.hits.hits[i].fields
            //Add Markers on Map
            var marker = L.marker([data.latitude[0], data.longitude[0]], {icon: neighborsIcon}).addTo(map);
            marker.bindPopup("<b>" + data.name + ": " + data.stars + "</b>").openPopup();

            neighborhood.push({'name': data.name[0], 'stars': data.stars[0], 'categories': data.categories,'num_reviews':data.review_count[0]})
        }
        console.log(neighborhood[0])

        // Crossfilter
        var ndx = crossfilter(neighborhood);
        var ndx1 = crossfilter(neighborhood);

        var starsDim = ndx.dimension(function(d) { return d.stars; });
        print_filter(starsDim.filter([1,2]));

        var countByStars = starsDim.group().reduceSum(function(d) {return 1;});
        print_filter(countByStars);


        chart = dc.barChart("#viz_neighborhood_stars");
        chart
            .width(600)
            .height(380)
            .x(d3.scale.ordinal())
            .xUnits(dc.units.ordinal)
            .elasticX(true)
            .elasticY(true)
            .brushOn(false)
            .colors('#FF430D')
            .gap(10)
            .xAxisLabel("Star Ratings of Neighborhood Business")
            .yAxisLabel("Count")
            //.xAxis().tickFormat(function(d) {return day_of_week(d.day)})
            .dimension(starsDim)
            .group(countByStars)
        chart.render();



        function reduceAdd(p, v) {
            if (v.categories[0] === "") return p;    // skip empty values
            v.categories.forEach (function(val, idx) {
                p[val] = (p[val] || 0) + 1; //increment counts
            });
            return p;
        }

        function reduceRemove(p, v) {
            if (v.categories[0] === "") return p;    // skip empty values
            v.categories.forEach (function(val, idx) {
                p[val] = (p[val] || 0) - 1; //decrement counts
            });
            return p;

        }

        function reduceInitial() {
            return {};
        }


        var categoriesDim = ndx1.dimension(function(d){ return d.categories;});
        var categoriesGroup = categoriesDim.groupAll().reduce(reduceAdd, reduceRemove, reduceInitial).value();
        // hack to make dc.js charts work
        categoriesGroup.all = function() {
            var newObject = [];
            for (var key in this) {
                if (this.hasOwnProperty(key) && key != "all" && key != "top") {
                    newObject.push({
                        key: key,
                        value: this[key]
                    });
                }
            }
            return newObject;
        };

        categoriesGroup.top = function(count) {
            var newObject = this.all();
            newObject.sort(function(a, b){return b.value - a.value});
            return newObject.slice(0, count);
        };


        function remove_bins(source_group,rest_cat) { // (source_group, bins...}
            return {
                all:function () {
                    return source_group.all().filter(function(d) {
                        return rest_cat.indexOf(d.key) !== -1;
                    });
                }
            };
        }


        //console.log(categoriesGroup);
        var rest_cat = d.hits.hits[0].fields.categories
        var filtered_group = remove_bins(categoriesGroup,rest_cat)
        console.log(filtered_group)

        var barChart_cat = dc.rowChart("#cat_graph");
        barChart_cat
            .margins({
                top: 10,
                right: 30,
                bottom: 30,
                left: 60
            })
            .renderLabel(true)
            .width(500)
            .height(300)
            .elasticX(true)
            .dimension(categoriesDim)
            .colors('#FF430D')
            .group(filtered_group)
            .ordering(function(d){return -d.value;})
            .xAxis().ticks(3)
            ;
        barChart_cat
            .render();

        barChart_cat.filterHandler (function (dimension, filters) {
                dimension.filter(null);
                if (filters.length === 0)
                    dimension.filter(null);
                else
                    dimension.filterFunction(function (d) {
                        for (var i=0; i < d.length; i++) {
                            if (filters.indexOf(d[i]) >= 0) return true;
                        }
                        return false;
                    });
                return filters;
            }
        );

//					Scatter plot for restaurants in category
        var sctr_chart = dc.scatterPlot("#detail_cat_graph");
        var ratingDim = ndx1.dimension(function(d){ return [d.stars, d.num_reviews];});
        var ratingGroup = ratingDim.group().reduceSum(function(d){return d.num_reviews;});

        var minNum  = ratingDim.bottom(1)[0].num_reviews;
        var maxNum = ratingDim.top(1)[0].num_reviews;
        console.log(minNum,maxNum);

        sctr_chart
            .margins({
                top: 10,
                right: 30,
                bottom: 30,
                left: 60
            })
            .renderLabel(true)
            .width(600)
            .height(300)
            .transitionDuration(800)
            .elasticX(true)
            .xUnits(dc.units.ordinal)
            .colors('#FF430D')
            .x(d3.scale.ordinal().domain(d3.range(5)))
            .dimension(ratingDim)
            .group(ratingGroup)
            .brushOn(false)
            .xAxisLabel("Star Rating")
            .symbolSize(5)
            ._rangeBandPadding(1)
            .clipPadding(5);
        sctr_chart
            .yAxisLabel("Number of reviews");

        sctr_chart.render();



    })
        //.header("Content-Type","application/json")
        //.send("POST", url_2)

})
    //.header("Content-Type","application/json")
    //.send("POST", url_1)
