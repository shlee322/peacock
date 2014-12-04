var peacock = require('./peacock.js');

peacock.init(function(err){
  if(err) {
    console.log('error! ' + err);
    return;
  }

  peacock.createHttpServer('test_server_1', function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello World\n');
  }).listen(8080, '127.0.0.1');
});


console.log('Server running at http://127.0.0.1:8080/');