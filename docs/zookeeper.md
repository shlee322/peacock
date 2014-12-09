주키퍼의 노드는 다음과 같이 구성한다.

/peacock/logger/zmq
 - /node??? - ephemeral, sequence : 로거의 BIND 주소들을 저장

/peacock/job/nodes
 - /node??? - ephemeral, sequence : 로거의 BIND 주소들을 저장

NODE 갯수를 구하고 8192/node갯수 하여 그 큐를 처리하도록 함
