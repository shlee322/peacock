var socket = new WebSocket('ws://' + location.hostname + ':7000/' + service_id);
var subscribe_list = {};
/*
setInterval(function() {
    var now =  new Date().getTime()/1000;
    for(var name in subscribe_list){
        var subscribe = subscribe_list[name];
        for(var i in subscribe) {
            var graph = subscribe[i];
            /*
            graph.graph.series[0].data.push({
                'x': now,
                'y': -1
            });
//*
            graph.graph.series[0].data = jQuery.grep(graph.graph.series[0].data, function(value) {
                return (now-600) < value.x;
            });

            graph.graph.update();
        }
    }
}, 1000);
*/


socket.onmessage = function (data) {
    var message = JSON.parse(data.data);

    var subscribe_obj = subscribe_list[message.analyzer_name];
    if(!subscribe_obj) return;

    subscribe_obj.data[message.data.group[0] + "_" + message.data.group[1]] = message.data;

    for(var i=0; i<subscribe_obj.funcs.length; i++) {
        subscribe_obj.funcs[i](subscribe_obj, message.data.group[0] + "_" + message.data.group[1]);
    }
};

function get_subscribe(analyzer_name) {
    return subscribe_list[analyzer_name];
}

function add_subscribe(analyzer_name, func, start, end) {
    if(subscribe_list[analyzer_name]) {
        subscribe_list[analyzer_name].funcs.push(func);
        return;
    }

    if(!end) end = null;

    subscribe_list[analyzer_name] = {
        'analyzer_name': analyzer_name,
        'timestamp': {
            'start': start,
            'end': end
        },
        'data': {},
        'funcs': [func]
    };

    socket.send(JSON.stringify({
        'type': 'subscribe',
        'target': {
            'analyzer_name': analyzer_name,
            'timestamp': {
                'start': start,
                'end': end
            }
        }
    }));
}

/*
function add_bar_graph(id, width, height, analyzer_name, series, func) {
    var element = document.getElementById(id);
/*
    var graph = new Rickshaw.Graph( {
        element: element,
        width: width,
        height: height,
        renderer: 'bar',
        series: []
    });

    graph.render();

    add_subscribe('damage', function(subscribe, group){
        console.log(subscribe);
    }, new Date().getTime() - 3600000, null);
}




/*
if(!subscribe_list[message.analyzer_name]) return;

var list = subscribe_list[message.analyzer_name];

var data_list = message.data.data;
for(var i in list) {
    var graph = list[i];

    for(var data_i in data_list) {
        var data = graph.func(data_list[data_i]);
        graph.graph.series[data.type].data.push(data);
    }

    graph.graph.update();
}
*/

/*
function add_plot_graph(id, width, height, analyzer_name, series, func) {
    add_graph('scatterplot', id, width, height, analyzer_name, series, func);
}

function add_line_graph(id, width, height, analyzer_name, series, func) {
    add_graph('line', id, width, height, analyzer_name, series, func);
}


function add_graph(type, id, width, height, analyzer_name, series, func) {
    if(!subscribe_list[analyzer_name]) {
        subscribe_list[analyzer_name] = []
    }


    var element = document.getElementById(id);

    var now =  new Date().getTime()/1000;/*
    for(var i=600; i>=0; i--) {
        series.push({
            'x': now-i,
            'y': -1
        })
    }
    series.push({
        'x': now,
        'y': 0
    });
*/
/*
    var graph = new Rickshaw.Graph( {
        element: element,
        width: width,
        height: height,
        renderer: type,
        series: series
    });

    subscribe_list[analyzer_name].push({
        'graph': graph,
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

    var time = new Rickshaw.Fixtures.Time();
    var seconds = time.unit('15 second');

    var xAxis = new Rickshaw.Graph.Axis.Time({
        graph: graph,
        timeUnit: seconds
    });

    xAxis.render();

    var yAxis = new Rickshaw.Graph.Axis.Y({
        graph: graph
    });

    yAxis.render();

    var hoverDetail = new Rickshaw.Graph.HoverDetail( {
        graph: graph,
        onShow: function(event){

        }
    } );
}
*/