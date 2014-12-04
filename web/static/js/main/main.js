function validateEmail(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
}

peacock.controller('loginController', function($scope, $http) {
    $scope.formData = {};
    $scope.alerts = [];

    $scope.submit = function() {
        $scope.alerts = [];

        if(!$scope.formData.username || $scope.formData.username == '') {
            $scope.alerts.push({
                'type':'warning',
                'msg': '아이디를 입력해주세요'
            });
            return;
        }

        if(!$scope.formData.password || $scope.formData.password == '') {
            $scope.alerts.push({
                'type':'warning',
                'msg': '비밀번호를 입력해주세요'
            });
            return;
        }

        $http.post('/_ajax/login', $scope.formData).success(function(data){
            if(data.status == 'failed') {
                $scope.alerts.push({
                    'type':'danger',
                    'msg': data.message
                });
                return;
            }

            //test
        });
    }
});

peacock.controller('joinController', function($scope, $http) {
    $scope.formData = {};
    $scope.alerts = [];

    $scope.submit = function() {
        $scope.alerts = [];

        if(!$scope.formData.username || $scope.formData.username == '') {
            $scope.alerts.push({
                'type':'warning',
                'msg': '아이디를 입력해주세요'
            });
            return;
        }

        if(!$scope.formData.password || $scope.formData.password == '') {
            $scope.alerts.push({
                'type':'warning',
                'msg': '비밀번호를 입력해주세요'
            });
            return;
        }

        if(!$scope.formData.confirm_password || $scope.formData.confirm_password == '') {
            $scope.alerts.push({
                'type':'warning',
                'msg': '비밀번호 확인 값을 입력해주세요'
            });
            return;
        }

        if(!$scope.formData.email || $scope.formData.email == '') {
            $scope.alerts.push({
                'type':'warning',
                'msg': '이메일을 입력해주세요'
            });
            return;
        }

        if($scope.formData.password != $scope.formData.confirm_password) {
            $scope.alerts.push({
                'type':'danger',
                'msg': '비밀번호와 비밀번호 확인 값이 일치하지 않습니다'
            });
            return;
        }

        if(!validateEmail($scope.formData.email)) {
            $scope.alerts.push({
                'type':'danger',
                'msg': '이메일 형식이 올바르지 않습니다'
            });
            return;
        }

        $http.post('/_ajax/join', $scope.formData).success(function(data){
            if(data.status == 'failed') {
                $scope.alerts.push({
                    'type':'danger',
                    'msg': data.message
                });
                return;
            }

            //test
        });
    }
});

