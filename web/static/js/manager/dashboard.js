peacock.config(function(WebSocketProvider){
    WebSocketProvider
      .prefix('')
      .uri("ws://localhost:7000/" + service_id);
});

peacock.controller('dashboardController', function($scope, $filter, $modal, $http, WebSocket) {
    var test = [];
    test.push({
        'type': 'subscribe',
        'viewer_id': 'aaaa',
        'target': {
            'type': 'event',
            'entity_kind': 'response',
            'event_name': 'response',
            'timestamp': {
                'start': new Date().getTime() - 10*60*1000
            }
        }
    });

    WebSocket.onmessage(function(event) {
        var message = JSON.parse(event.data);
        if(message.type == 'subscribe_message') {

        }
    });

    WebSocket.onopen(function() {
        for(var i in test) {
            WebSocket.send(JSON.stringify(test[i]));
        }
    });

    /*
var seriesData = [ [], [], [], [], [], [], [], [], [] ];
var random = new Rickshaw.Fixtures.RandomData(300);

for (var i = 0; i < 300; i++) {
	random.addData(seriesData);
}

var palette = new Rickshaw.Color.Palette( { scheme: 'classic9' } );

var graph = new Rickshaw.Graph( {
	element: document.getElementById("chart"),
	width: 900,
	height: 500,
	renderer: 'scatterplot',
} );

graph.render();

var xAxis = new Rickshaw.Graph.Axis.Time({
    graph: graph
});

xAxis.render();

var yAxis = new Rickshaw.Graph.Axis.Y({
    graph: graph
});

yAxis.render();*/
});