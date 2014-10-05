var express = require('express');
var handlers = require("./handlers");

var app = express();
app.use(express.bodyParser());

app.use(function (req, res, next) {

    // Website you wish to allow to connect
    res.setHeader('Access-Control-Allow-Origin', 'http://localhost');

    // Request methods you wish to allow
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');

    // Request headers you wish to allow
    res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');

    // Set to true if you need the website to include cookies in the requests sent
    // to the API (e.g. in case you use sessions)
    res.setHeader('Access-Control-Allow-Credentials', true);

    // Pass to next layer of middleware
    next();
});


app.get('/', function(req, res) {
  res.send('please select a collection, e.g., /collections/messages');
});

app.get('/LDRLY/', handlers.root);
app.post('/LDRLY/sendStat', handlers.sendStat);
app.put('/LDRLY/sendStat', handlers.sendStat);
app.get('/LDRLY/getLeaderboard', handlers.getLeaderboard);
app.get('/LDRLY/getStats', handlers.getStats);

app.listen(3000);