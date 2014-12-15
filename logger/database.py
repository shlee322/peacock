from couchbase.bucket import Bucket as CouchbaseBucket

event_db = CouchbaseBucket('couchbase://localhost/events')
link_db = CouchbaseBucket('couchbase://localhost/links')
analyzer_db = CouchbaseBucket('couchbase://localhost/analyzers')
analyzer_input_db = CouchbaseBucket('couchbase://localhost/analyzer_input')
analyzer_result_db = CouchbaseBucket('couchbase://localhost/analyzer_result')
server_token_db = CouchbaseBucket('couchbase://localhost/server_token')
