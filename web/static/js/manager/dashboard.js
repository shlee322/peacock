var socket = new WebSocket('ws://' + location.hostname + ':7000/' + service_id);
var subscribe_list = {};

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

function show_graph(config) {
    var element = document.getElementById(config.element);
    var graph = new Rickshaw.Graph( {
        element: element,
        width: config.width,
        height: config.height,
        renderer: config.renderer,
        series: config.series
    });
    graph.render();

    var time = new Rickshaw.Fixtures.Time();

    var xAxis = new Rickshaw.Graph.Axis.Time({
        graph: graph,
        timeUnit: time.unit(config.x_time)
    });

    xAxis.render();

    var yAxis = null;
    if(config.y_format == 'kmbt') {
        yAxis = new Rickshaw.Graph.Axis.Y({
            graph: graph,
            tickFormat: Rickshaw.Fixtures.Number.formatKMBT
        });
    } else{
        yAxis = new Rickshaw.Graph.Axis.Y({
            graph: graph
        });
    }

    yAxis.render();

    var hoverDetail = new Rickshaw.Graph.HoverDetail( {
        graph: graph
    } );

    var update_graph = function(){
        var start_time = new Date().getTime() - config.range;

        var subscribe = get_subscribe(config.analyzer_name);

        var temp = {};
        graph.series[0].data = [];
        for(var name in subscribe.data) {
            var obj = subscribe.data[name];
            temp[obj.group[0]] = true;

            var result = config.func(obj);
            if(!result) continue;

            graph.series[result.type].data.push({
                x:obj.group[result.type]/1000,
                y:obj.data,
                xFormatter: function(x) { return "load"; },
                yFormatter: function(y) { return y.toString(); }
            });
        }

        var test = Math.floor(new Date().getTime()/config.group) * config.group;
        var chart_start_time = Math.floor(start_time/config.group) * config.group;

        for(var time=chart_start_time; time<=test; time+=config.group) {
            if(!temp[time]) {
                graph.series[0].data.push({
                    x:time/1000,
                    y:0
                });
            }
        }

        for(var i=0; i<graph.series.length; i++) {
            graph.series[i].data = jQuery.grep(graph.series[i].data, function (obj) {
                return start_time < obj.x*1000;
            });
            graph.series[i].data.sort(function (a, b){
                return a.x - b.x;
            });
        }

        graph.update();
    };

    add_subscribe(config.analyzer_name, function(subscribe, group){
        update_graph();
    }, new Date().getTime() - config.range, null);

    setInterval(update_graph, config.group);
    update_graph();
}
