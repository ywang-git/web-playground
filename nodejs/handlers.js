var mongoskin = require('mongoskin');

var db = mongoskin.db('localhost:27017/test', {safe:true});

function root(request, response) {
	var body = '<html>\n';
	body += '<html>\n';
	body += '<form name="input" action="/LDRLY/sendStat" method="post">\n';
	body += 'Username: <input type="text" name="username">\n';
	body += 'Stat Name: <input type="text" name="statname">\n';
	body += 'Stat Value: <input type="text" name="statvalue">\n';
	body += '<input type="submit" value="Submit">\n';
	body += '</form>\n';
	body += '<html />\n';
	
	response.send(body);
}

function sendStat(request, response) {
	console.log("Request handler 'sendStat' was called.");
	
	var statvalue = parseInt(request.body.statvalue);
	
	// validate the input data
	if (statvalue && request.body.username && request.body.statname) {

		// update the document, create if not exist
		db.collection('user_stats').update(
			{"username" : request.body.username, 
			"statname" : request.body.statname}, 
			{$set : {"statvalue" : statvalue}}, 
			{upsert : true}, function(err, result) {
				if (result) {
					console.log(result);
				}
				else {
					response.status(500).send("Server Error.");
				}
			});	
		// return the updated entry
		db.collection('user_stats').findOne({"username" : request.body.username,
			"statname" : request.body.statname}, function(err, result){
				if (result) {
    				console.log(result);
			  		response.set('Content-Type', 'application/json');
    				response.set({'ETag' : result});
					response.status(201).send(result);
				}
				else {
					response.status(500).send("Server Error.");
				}
		  });
	}
	else
	{
		response.status(400).send("invalid input data");
	}
}

function getLeaderboard(request, response) {
  console.log("Request handler 'getLeaderboard' was called.");  

  db.collection('user_stats').find({"statname" : request.query.statname},
  {"sort" : [["statvalue",'desc']]}).toArray(function(err, results){
  	// adding the rank field
  	if (results) {
	  	for (i = 0; i < results.length; ++i) {
  			results[i].rank = i + 1;
  		}
  		response.set('Content-Type', 'application/json');
		response.status(200).send(results);
  	}
  	else {
  		response.status(500).send("Server Error.");
  	}
  });
}

function getStats(request, response) {
  console.log("Request handler 'getStats' was called.");
  
  db.collection('user_stats').find({"username" : request.query.username})
  .toArray(function(err, results){
  	if (results) {
  		response.set('Content-Type', 'application/json');
  		response.status(200).send(results);
  	}
  	else {
  		response.status(500).send("Server Error.");
  	}
  });
}

exports.root = root;
exports.sendStat = sendStat;
exports.getLeaderboard = getLeaderboard;
exports.getStats = getStats;
