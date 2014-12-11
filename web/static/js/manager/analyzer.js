peacock.controller('addAnalyzerController', function($scope, $filter, $modal, $http) {
    $scope.inputList = [];

    $scope.isAddEditView = true;
    $scope.addInputEvent = {};
    $scope.addInputAnalyzer = {};
    $scope.isGroupView = true;

    $scope.addAnalyzer = {};
    $scope.addAnalyzer.group_time = 0;

    $scope.addInputEvent.submit = function() {
        $scope.inputList.push({
            'type':'event',
            'kind': $scope.addInputEvent.kind,
            'id': $scope.addInputEvent.id
        });

        $scope.addInputEvent.kind = '';
        $scope.addInputEvent.id = '';
    };
    $scope.addInputAnalyzer.submit = function() {
        $scope.inputList.push({
            'type':'analyzer',
            'name': $scope.addInputAnalyzer.name
        });

        $scope.addInputAnalyzer.name = '';
    };

    $scope.addAnalyzer.submit = function() {
        console.log("ASFdfd");
        var data = {
            'name': $scope.addAnalyzer.name,
            'input': $scope.inputList,
            'group': {
                'time': Number($scope.addAnalyzer.group_time),
                'entity_kind': $scope.addAnalyzer.group_entity_kind
            },
            'processor_script': $scope.addAnalyzer.processor_script
        };

        $http.post('/manager/' + service_id + '/analyzer/_ajax/add_analyzer', data).success(function(data){
            if(data.status == 'failed') {
                $scope.alerts.push({
                    'type':'danger',
                    'msg': data.message
                });
                return;
            }

            document.location = '/manager/' + service_id + '/analyzer';
        });
    };
});