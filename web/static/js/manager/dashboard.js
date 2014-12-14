peacock.config(function(WebSocketProvider){
    WebSocketProvider
      .prefix('')
      .uri("ws://localhost:7000/" + service_id);
});

peacock.controller('dashboardController', function($scope, $filter, $modal, $http, WebSocket) {
    var test = [];
    test.push({
        'type': 'subscribe',
        'target': {
            'type': 'event',
            'entity_kind': 'response',
            'event_name': 'response',
            'timestamp': {
                'start': new Date().getTime() - 10*60*1000
            }
        }
    });

    WebSocket.onopen(function() {
        console.log('connection');

        for(var i in test) {
            WebSocket.send(JSON.stringify(test[i]))
        }

    });

    WebSocket.onmessage(function(event) {
        console.log('message: ', event.data);
    });
});