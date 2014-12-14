var socket = new WebSocket('ws://' + location.hostname + ':7000/' + service_id);
var subscribe_list = {};

socket.onmessage = function (data) {
    var message = JSON.parse(data.data);


    if(!subscribe_list[message.analyzer_name]) return;

    var list = subscribe_list[message.analyzer_name];

    var data_list = message.data.data;
    for(var i in list) {
        var graph = list[i];

        for(var data_i in data_list) {
            graph.series.push(graph.func(data_list[data_i]));
        }

        graph.graph.update();
    }
};

function add_plot_graph(id, width, height, analyzer_name, func) {
    if(!subscribe_list[analyzer_name]) {
        subscribe_list[analyzer_name] = []
    }


    var element = document.getElementById(id);

    var series = [];

    var graph = new Rickshaw.Graph( {
        element: element,
        width: width,
        height: height,
        renderer: 'scatterplot',
        series: [{
            color: 'steelblue',
            data: series
        }]
    });

    subscribe_list[analyzer_name].push({
        'graph': graph,
        'series': series,
        'func': func
    });

    graph.render();

    socket.send(JSON.stringify({
        'type': 'subscribe',
        'target': {
            'analyzer_name': analyzer_name,
            'timestamp': {
                'start': new Date().getTime() - 10*60*1000
            }
        }
    }));

    var xAxis = new Rickshaw.Graph.Axis.Time({
        graph: graph
    });

    xAxis.render();

    var yAxis = new Rickshaw.Graph.Axis.Y({
        graph: graph
    });

    yAxis.render();
}