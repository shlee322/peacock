var os = require('os');
var peacock = require('./peacock.js');

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

  var server_entity = new peacock.Entity('server', 'test_server_1');

  var cpus = os.cpus();
  for(var i=0; i<cpus.length; i++) {
      var cpu_entity = new peacock.Entity('cpu_state', 'test_server_1_cpu_' + i);
      cpu_entity.link(server_entity);
  }
  var mem_entity = new peacock.Entity('mem_state', 'test_server_1');
  mem_entity.link(server_entity);

  var last_time = new Date();

  setInterval(function (){
    var now_time = new Date();
    var cpus = os.cpus();
    for(var i=0; i<cpus.length; i++) {
      var cpu_entity = new peacock.Entity('cpu_state', 'test_server_1_cpu_' + i);
      cpu_entity.event('cpu_state', cpus[i].times, now_time, last_time);
    }

    mem_entity.event('mem_state', {
      'total':os.totalmem(),
      'free':os.freemem()
    }, now_time, last_time);

    last_time = now_time;
  }, 5000);
});

console.log('Server running at http://127.0.0.1:8080/');
