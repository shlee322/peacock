peacock.controller('eventViewerController', function($scope, $filter, $modal, $http) {
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
        $http.get('/manager/' + service_id + '/eventviewer/_ajax/get_event_list?timestamp='+now_date)
            .success(function (data){
                $scope.event_list = data.data;
        });
    };

    $scope.load_log();
});