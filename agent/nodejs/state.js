var os = require('os');
var peacock = require('./peacock.js');
var libCpuUsage = require('cpu-usage');


var options = {
  'key_file': __dirname + '/test_private.pem',
  'service_id': 'kr-elab-test',
  'server_key_id': 'test_key'
};

peacock.init(options, function(err){
  if(err) {
    console.log(err);
    return;
  }

  var server_entity = new peacock.Entity('server_state', 'test_server_1');

  var last_time = new Date();

  libCpuUsage(5000, function(load) {
    var now_time = new Date();

    server_entity.event('cpu', load, now_time, last_time); 
    server_entity.event('memory', {
      'total':os.totalmem(),
      'free':os.freemem()
    }, now_time, last_time);

    last_time = now_time;
  });
});

console.log('Server running at http://127.0.0.1:8080/');
