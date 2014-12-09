peacock.controller('eventViewerController', function($scope, $filter, $modal, $http) {
    $scope.formData = {};

    $scope.view_entity = function (kind, id, timestamp) {
        openEntityModal($modal, kind, id, timestamp);
    };

    $scope.load_log = function (timestamp, start_timestamp) {
        $http.get('/manager/' + service_id + '/eventviewer/_ajax/get_event_list?timestamp='+ timestamp + '&start_timestamp=' + start_timestamp)
            .success(function (data){
                $scope.event_list = data.data.concat($scope.event_list);
        });
    };

    $scope.load_log(new Date().getTime(), 0);
});