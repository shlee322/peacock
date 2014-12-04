var AUTH_URL = 'http://localhost:5000/auth';

function initPeacock(cb) {
    var request = require('request');

    var options = {
      uri: AUTH_URL,
      method: 'POST',
      json: {
      }
    };

    request(options, function (error, response, body) {
        if(error) {
            cb(error);
            return;
        }

        if(response.statusCode != 200) {
            cb(response.statusCode);
            return;
        }

        cb();
    });
}

function Entity(kind, id) {
    this.kind = kind;
    this.id = id;
}

Entity.prototype.link = function(entity) {
    console.log('link ' + this.kind + ' - ' + entity.kind);
};

Entity.prototype.unlink = function(entity) {
    console.log('unlink ' + this.kind + ' - ' + entity.kind);
};

Entity.prototype.event = function (name, data, date, date2) {
    if(!date) {
        date = new Date();
    }

    console.log('event' + this.kind + ' ' + name);
};

var seq = 0;

function createPeacockHttpProxy(server_id, requestListener) {
    var server_entity = new Entity('server', server_id);
    var request_path_kind = 'request_path';
    var request_entity_kind = 'request';
    var response_entity_kind = 'request';

    var originalRequestListener = requestListener;

    var peacockRequestListener = function(req, res) {
        var end_method = res.end;
        res.end = function() {
            var time = new Date();
            res._peacock_response_entity = new Entity(response_entity_kind, time.getTime() + '_' + server_id + '_' + seq++);
            req._peacock_request_entity.link(res._peacock_response_entity);

            res._peacock_response_entity.event('response', {
                'statusCode': res.statusCode
            }, time, req._peacock_request_time);

            req._peacock_request_entity.unlink(res._peacock_response_entity);
            req._peacock_request_entity.unlink(req._peacock_request_path_entity);
            req._peacock_request_entity.unlink(server_entity);

            end_method.apply(res, arguments);
        };

        req._peacock_request_time = new Date();

        req._peacock_request_path_entity = new Entity(request_path_kind, require('url').parse(req.url).pathname);
        req._peacock_request_entity = new Entity(request_entity_kind, req._peacock_request_time.getTime() + '_' + server_id + '_' + seq++);
        req._peacock_request_entity.link(server_entity);
        req._peacock_request_entity.link(req._peacock_request_path_entity);

        req._peacock_request_entity.event('request', {
            'httpVersion': req.httpVersion,
            'headers': req.headers,
            'method': req.method,
            'url': req.url
        }, req._peacock_request_time);

        originalRequestListener(req, res);
    };

    return peacockRequestListener;
}

function createHttpServer(server_id, requestListener){
    return require('http').createServer(createPeacockHttpProxy(server_id, requestListener));
}

function createHttpsServer(options, server_id, requestListener){
    return require('https').createServer(options, createPeacockHttpProxy(server_id, requestListener));
}

var exports = module.exports = {};
exports.init = initPeacock;
exports.Entity = Entity;
exports.createHttpServer = createHttpServer;
exports.createHttpsServer = createHttpsServer;
