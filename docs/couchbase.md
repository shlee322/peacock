[Data Bucket] analyzer_input
-----------------

Views

- input -> event

```javascript
function (doc, meta) {
  emit([doc.service.id, doc.analyzer_id,  doc.event_id, doc.group[0], doc.group[1]], doc);
}
```


- input -> group

```javascript
function (doc, meta) {
  emit([doc.service.id, doc.analyzer_id, doc.group[0], doc.group[1], doc.event_id], doc.event_id);
}
```


Simple Document

```json
{
  "event_id": "1418364430198_node0000000010_1",
  "group": [
    1418364430,
    "1418364430179_test_server_1_106"
  ],
  "analyzer_id": "3d637aa507821693aeb1a63e86f07cec1cea587b4e731e8e6cc5acbf6e8066d7",
  "service": {
    "id": "kr-elab-test"
  }
```


[Data Bucket] analyzer_result
-----------------

Views

- monitor -> monitor

```javascript
function (doc, meta) {
  emit([doc.analyzer_id, doc.group[0], doc.group[1]], doc);
}
```


Simple Document

```json
{
   "data": 38,
   "analyzer_id": "a5c6bc965c7f6729c748555f829c81fbbace9e59ed80800a98f9136c5db23713",
   "service": {
       "id": "kr-elab-test"
   },
   "group": [
       1418646746000,
       "test_server_1"
   ]
}
```

[Data Bucket] analyzers
-----------------

Views

- analyzers -> analyzer_list

```javascript
function (doc, meta) {
  emit([doc.service.id, doc.name], doc);
}
```


- analyzers -> event_to_analyzer

```javascript
function (doc, meta) {
  for(var i=0; i<doc.input.length; i++) {
      if(doc.input[i].type == "event") emit([doc.service.id, doc.input[i].kind, doc.input[i].id, meta.id], doc);
  }
}
```


Simple Document

```json
{
   "input": [
       {
           "kind": "server_state",
           "type": "event",
           "id": "memory"
       }
   ],
   "service": {
       "id": "kr-elab-test"
   },
   "name": "memory",
   "processor_script": "input[0].data.total - input[0].data.free",
   "group": {
       "entity_kind": "server_state",
       "time": 5000
   }
}
```


[Data Bucket] events
-----------------

Views

- events -> entity_timeline

```javascript
function (doc, meta) {
  if(doc.type != "event") return;
  emit([doc.service.id, doc.entity.kind, doc.entity.id, doc.timestamp, meta.id], doc);
}
```


- events -> eventviewer

```javascript
function (doc, meta) {
  if(doc.type != "event") return;
  emit([doc.service.id, doc.timestamp, meta.id], doc);
}
```


Simple Document

```json
{
   "data": {
       "y": 76,
       "x": 42
   },
   "type": "event",
   "service": {
       "id": "kr-elab-test"
   },
   "log_key": "1418636003242_node0000000019_1",
   "event_name": "spawn",
   "entity": {
       "id": "71151",
       "kind": "mob"
   },
   "timestamp": 1418635986996
}
```


[Data Bucket] links
-----------------

Views

- links -> timeline
```javascript
function (doc, meta) {
  emit([doc.service.id, doc.entity.kind, doc.entity.id, doc.timestamp], doc);
}
```


Simple Document

```json
{
   "timestamp": 1418572878564,
   "links": [
       {
           "timestamp": 1418572878564,
           "id": "/favicon.ico",
           "kind": "request_path",
           "count": 0
       },
       {
           "timestamp": 1418572878564,
           "id": "1418572878564_test_server_1_71",
           "kind": "response",
           "count": 0
       }
   ],
   "service": {
       "id": "kr-elab-test"
   },
   "entity": {
       "id": "1418572878563_test_server_1_70",
       "kind": "request"
   }
}
```

[Data Bucket] server_token

Simple Document

```json
{
  "server": "test_key",
  "key": "e31e39364cb09a86f8d42929a5d0c641",
  "service": {
    "id": "kr-elab-test"
  }
}
```
