/*
You need to specify the following environmental variables in the lambda function:
- SMARTHOME_HOST
		foobar.dyndns.tld
- SMARHOME_PORT
		443 - endpoint must be https enabled!
- SMARTHOME_PATH
		'/'
- SMARTHOME_AUTH
		'user:password'
*/
exports.handler = function(event, context, callback) {
	var data = 'json=' + JSON.stringify(event)

	var options = {
		hostname: process.env.SMARTHOME_HOST,
		port: process.env.SMARHOME_PORT,
		path: process.env.SMARTHOME_PATH,
		method: 'POST',
		auth: process.env.SMARTHOME_AUTH,
		headers: {
			'Content-Type': 'application/json',
			'Content-Length': Buffer.byteLength(data)
		}
	};

	var https = require('https');
	var req = https.request(options, (res) => {
		console.log(`request: ${res.statusCode} / ${JSON.stringify(res.headers)}`);
		res.setEncoding('utf8');
		if (res.statusCode != 200) {
			callback(`DependentServiceUnavailableError`);
			return;
		}

		var dataChunks = [];
		res.on('data', (chunk) => dataChunks.push(chunk)).on('end', () => {
			var responseData = Buffer.concat(dataChunks).toString();
			console.log(`response: ${responseData}`)

			var noError = null;
			var response = JSON.parse(responseData);
			callback(noError, response);
		});
	});
	req.on('error', (e) => {
		console.log(`request failed: ${e.message}`);
		callback(e);
	});
	req.write(data);
	req.end();
}
