#LDRLY User Stats Demo#
##Description of Files##
* nodejs: Server source files and dependency libraries.
	* express.js: Main application file.
	* handlers.js: Web services requests handlers.
	* node_modules: Module dependencies.
		* mongoskin: MongoDB node.js wrapper.
		* express: express.js module.
* client: Web application demo.
	* index.html: Web page demostrating the 3 basic web services API.
* data: Scripts to generate test data.
	* gen_data.py: A python script to generate the test data set.
	* data.sh: A generated shell script to insert data through curl calls.
	
##Setup Instruction##

1. Set up MongoDB on localhost;
2. Set up node.js on localhost (since modules has been included, so there is no need to install mongoskin / express);
3. Set up a web server to host the client code;
4. Update the "Access-Control-Allow-Headers" setting in express.js accordingly, with the server domain you are going to use;
5. Use "mongodbd"" to start the database;
6. Use "node express.js" to start the web services;
7. Use "data.sh" to populate the data into the database;
8. Open the web page index.html in a browser.

Now user can input player name / stat name in the text fields on the web page to see the result. Updating / inserting data is also available. The region below is a console to display the result returned by the server for SendStat request.
