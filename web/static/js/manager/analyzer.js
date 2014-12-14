peacock.controller('addAnalyzerController', function($scope, $filter, $modal, $http) {
    $scope.view_analyzer = function(name) {
        $http.get('/manager/' + service_id + '/analyzer/_ajax/get_analyzer?name='+name).success(function(data){
            var analyzer_data = data.data;
            $scope.addAnalyzer.name = analyzer_data.name;
            $scope.inputList = analyzer_data.input;
            $scope.addAnalyzer.group_time = analyzer_data.group.time;
            $scope.addAnalyzer.group_entity_kind = analyzer_data.group.entity_kind;
            $scope.addAnalyzer.processor_script = analyzer_data.processor_script;
            $('#addAnalyzerModal').modal();
        });
    };

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

        $http.post('/manager/' + service_id + '/analyzer/_ajax/set_analyzer', data).success(function(data){
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