from couchbase.bucket import Bucket as CouchbaseBucket

event_db = CouchbaseBucket('couchbase://localhost/events')
analyzer_result_db = CouchbaseBucket('couchbase://localhost/analyzer_result')
