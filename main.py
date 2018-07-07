from flask import Flask, request, abort
import json
from hashlib import sha256
from google.appengine.ext import ndb

app = Flask(__name__)


class Entry(ndb.Model):
    hash = ndb.StringProperty()
    message = ndb.StringProperty()


@app.route('/messages/<hash>', methods=['GET'])
def messages_get(hash):
    query = Entry.query(Entry.hash == hash)
    query_results = query.get()
    if not query_results:
        abort(404)
    message = query_results.message
    return json.dumps(dict(message=message), indent=4) + '\n'


@app.route('/messages', methods=['POST'])
def messages():
    # Receive message
    message = request.data
    parsed = json.loads(message)
    if not isinstance(parsed, dict):
        abort(404)
    if 'message' not in parsed:
        abort(404)
    # Hash it and log it in datastore
    hashed = sha256(parsed['message'].encode()).hexdigest()
    item = Entry(hash=hashed, message=parsed['message'])
    item.put()
    # Return a json object
    ret = dict(digest=hashed)
    final = json.dumps(ret, indent=4) + '\n'
    return final


@app.errorhandler(404)
def page_not_found(error):
    return json.dumps(dict(err_msg="Message not found"), indent=4) + '\n', 404
