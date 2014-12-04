peacock.controller('loginController', function($scope, $http) {
    $scope.formData = {};
    $scope.alerts = [];

    $scope.submit = function() {
        $http.post('/_ajax/login', $scope.formData, function(data){
            console.log(data);
        });
    }
});