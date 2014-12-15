var AUTH_URL = 'http://localhost:5000/auth';

var TOKEN = null;
var AES_KEY = null;

var crypto = require('crypto');
var request = require('request');
var NodeRSA = require('node-rsa');
var msgpack = require('msgpack');
var zmq = require('zmq');
var sock = zmq.socket('req');

function initPeacock(config, cb) {
    var fs = require('fs');

    fs.readFile(config.key_file, 'utf-8', function (err, data) {
        if (err) {
            throw err;
        }

        var rsa_key = new NodeRSA(data);

        AES_KEY = crypto.randomBytes(32);

        var sign = rsa_key.sign(AES_KEY.toString('hex'), 'hex', 'hex');

        var options = {
            uri: AUTH_URL,
            method: 'POST',
            json: {
                'service_id': config.service_id,
                'server_key_id': config.server_key_id,
                'sign': sign,
                'crypto': 'aes256',
                'key': AES_KEY.toString('hex'),
                'mode': 'cbc'
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

            if(body.status != 'succeeded') {
                cb(body);
                return;
            }

            TOKEN = body.data.token;

            //이제 서버 접속
            connect_logger(body.data.logger.zmq, cb);
        });
    });
}

function connect_logger(servers, cb) {
    for(var i=0; i<servers.length; i++)
        sock.connect('tcp://' + servers[i]);
    cb();
}

function send_data(obj) {
    var aes_iv = crypto.randomBytes(16);
    var cipher = crypto.createCipheriv('aes-256-cbc', AES_KEY, aes_iv);

    var objdata = msgpack.pack(obj);
    var buffer = [cipher.update(objdata), cipher.final()];

    var data = [TOKEN, aes_iv.toString('hex'), objdata.length, Buffer.concat(buffer)];
    sock.send(msgpack.pack(data));
}

function Entity(kind, id) {
    this.kind = kind;
    this.id = id;
}

Entity.prototype.link = function(entity) {
    var time = new Date().getTime();
    send_data({
        'timestamp': time,
        'type': 'link',
        'entity': {
            'kind': this.kind,
            'id': this.id
        },
        'target': {
            'kind': entity.kind,
            'id': entity.id
        }
    });
};

Entity.prototype.unlink = function(entity) {
    var time = new Date().getTime();
    send_data({
        'timestamp': time,
        'type': 'unlink',
        'entity': {
            'kind': this.kind,
            'id': this.id
        },
        'target': {
            'kind': entity.kind,
            'id': entity.id
        }
    });
};

Entity.prototype.event = function (name, data, date, date2) {
    if(!date) {
        date = new Date();
    }

    var send_obj = {
        'timestamp': date.getTime(),
        'type': 'event',
        'entity': {
            'kind': this.kind,
            'id': this.id
        },
        'event_name': name,
        'data': data
    };

    if(date2) {
        send_obj['timestamp_length'] = date2.getTime() - date.getTime();
    }

    send_data(send_obj);
};

var seq = 0;

function createPeacockHttpProxy(server_id, requestListener) {
    var server_entity = new Entity('server', server_id);
    var request_path_kind = 'request_path';
    var request_entity_kind = 'request';
    var response_entity_kind = 'response';

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
