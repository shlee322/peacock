peacock.controller('addAnalyzerController', function($scope, $filter, $modal, $http) {
    $scope.inputList = [];

    $scope.isAddEditView = true;
    $scope.addInputEvent = {};
    $scope.addInputAnalyzer = {};

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
});