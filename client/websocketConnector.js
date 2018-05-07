//
// Start by establishing the socket connection like this:
//
// 		websocketConnector.initSocket("127.0.0.1", 8080);
//
// Once the connection is established (not immediate), you can send unlimited number of messages to the server like this:
//
//		websocketConnector.sendMessage(messageAsJavaScriptObject);
//
// Your messages should be regular JavaScript objects, formatted as follows:
//
// 		{
//          request:    "dumpAttachment",
//          attachment:  yourReportObject
//      }
//
// For the first message, you can combine the initialization and the sending processes like this:
//
//		websocketConnector.initAndSend("127.0.0.1", 8080, messageAsJavaScriptObject);
//
// In this case, the software will wait for a connection to be established, then send the message automatically.
// Afterwards, just use .sendMessage() for any further messages.


var websocketConnector = {
	socket: null,

};

websocketConnector.launchSocketRequest = function (wsUrl, onOpenCallback) {

    var protocol = 'http';

    var socket = new WebSocket(wsUrl, protocol);

    console.log("Requested a socket connection with " + wsUrl + " using " + protocol + " as protocol.");

    socket.onopen = function(event) {
        
        websocketConnector.socket = socket;
        
        console.log("Socket connection established.");

        // run a callback, if provided
        if (onOpenCallback) {
        	onOpenCallback();
        }
    }
    
    socket.onmessage = function (event) {
        console.log("Received data: " + event.data);
    }
    
    socket.onclose = function (event) {
    	websocketConnector.socket = null;
        console.log("Socket connection closed.");
    }

    socket.onerror = function (event) {
    	websocketConnector.socket = null;
        console.log("Socket error.")
    }
    
    // websocketConnector.socket = socket;
};

websocketConnector.sendMessage = function (messageObject) {

	if (websocketConnector.socket) {

		if (websocketConnector.socket.readyState == WebSocket.OPEN) {

            websocketConnector.socket.send(JSON.stringify(messageObject));

        } else {

            console.log("Cannot send message, socket isn't ready for data to be sent.")
        }

	} else {

		console.log("Cannot send message, socket connection not established.")
	}
};

websocketConnector.initSocket = function (ip, port, onOpenCallback) {

    // form the request
    var wsUrl = "ws://" + ip + ":" + port;
    
    // launch the request
    websocketConnector.launchSocketRequest(wsUrl, onOpenCallback);

};

websocketConnector.initAndSend = function (ip, port, messageObject) {

	websocketConnector.initSocket(ip, port, function () {
		websocketConnector.sendMessage(messageObject);
	});
};