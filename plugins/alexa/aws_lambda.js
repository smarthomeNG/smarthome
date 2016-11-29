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
	var data = JSON.stringify(event)

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
		console.log(`HTTP ${res.statusCode}`);
		res.setEncoding('utf8');

		var responseData = '';
		res.on('data', (dataChunk) => {
		    responseData += dataChunk
		});
		res.on('end', () => {
			console.log(`response: ${responseData}`)
			var response = JSON.parse(responseData);

			if (res.statusCode == 200) {
				callback(null, response);
			} else {
				callback(`DependentServiceUnavailableError`);
			}
		});
	});
	req.on('error', (e) => {
		console.log(`request failed: ${e.message}`);
		callback(e);
	});
	req.write(data);
	req.end();
}
