peacock.controller('createServiceController', function($scope, $http) {
    $scope.formData = {};
    $scope.alerts = [];

    $scope.submit = function() {
        $scope.alerts = [];

        if(!$scope.formData.service_id || $scope.formData.service_id == '') {
            $scope.alerts.push({
                'type':'warning',
                'msg': 'Service ID를 입력해주세요'
            });
            return;
        }

        if(!$scope.formData.service_name || $scope.formData.service_name == '') {
            $scope.alerts.push({
                'type':'warning',
                'msg': 'Service Name를 입력해주세요'
            });
            return;
        }

        $http.post('/manager/create/_ajax/create', $scope.formData).success(function(data){
            if(data.status == 'failed') {
                $scope.alerts.push({
                    'type':'danger',
                    'msg': data.message
                });
                return;
            }

            document.location = '/manager/' + $scope.formData.service_id + '/';
        });
    }
});
