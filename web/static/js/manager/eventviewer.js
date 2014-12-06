peacock.config(function(WebSocketProvider){
    WebSocketProvider
      .prefix('')
      .uri("ws://localhost:7000/" + service_id);
  });

peacock.controller('eventViewerController', function($scope, $filter, $modal, WebSocket) {
    $scope.formData = {};

    $scope.view_entity = function (kind, id, timestamp) {
        openEntityModal($modal, kind, id, timestamp);
    };

    var now_date = new Date().getTime();
    $scope.formData.date = $filter('date')(now_date, 'yyyy-MM-dd');
    $scope.formData.time = $filter('date')(now_date, 'HH:mm:ss');

    $scope.time_previous = function() {
        now_date = $scope.event_list[0].timestamp;
        $scope.formData.date = $filter('date')(now_date, 'yyyy-MM-dd');
        $scope.formData.time = $filter('date')(now_date, 'HH:mm:ss');
        $scope.load_log();
    };

    $scope.time_next = function() {
        now_date = $scope.event_list[$scope.event_list.length - 1].timestamp;
        $scope.formData.date = $filter('date')(now_date, 'yyyy-MM-dd');
        $scope.formData.time = $filter('date')(now_date, 'HH:mm:ss');
        $scope.load_log();
    };

    $scope.load_log = function () {
        WebSocket.send(JSON.stringify({
            'method': 'get_event_list',
            'timestamp': now_date
        }));
    };

    WebSocket.onopen(function()
    {
        $scope.load_log();
    });

    WebSocket.onmessage(function (evt)
    {
        var received_msg = evt.data;
        var data = JSON.parse(received_msg);
        if(data.results.length > 0) $scope.event_list = data.results;
    });
});