peacock.controller('addServerController', function($scope, $http) {
    $scope.formData = {};
    $scope.alerts = [];

    $scope.submit = function() {
        $scope.alerts = [];

        if(!$scope.formData.id || $scope.formData.id == '') {
            $scope.alerts.push({
                'type':'warning',
                'msg': 'ID를 입력해주세요'
            });
            return;
        }

        if(!$scope.formData.key || $scope.formData.key == '') {
            $scope.alerts.push({
                'type':'warning',
                'msg': 'Public Key를 입력해주세요'
            });
            return;
        }

        $http.post('/manager/' + service_id + '/setting/_ajax/add_server', $scope.formData).success(function(data){
            if(data.status == 'failed') {
                $scope.alerts.push({
                    'type':'danger',
                    'msg': data.message
                });
                return;
            }

            document.location = '/manager/' + service_id + '/setting';
        });
    }
});
