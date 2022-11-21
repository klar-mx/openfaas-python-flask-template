#!/usr/bin/env python
from flask import Flask, request
from waitress import serve
import os


app = Flask(os.environ.get('FLASK_APP', __name__.split('.')[0]))
app.app_context().push()

# Import this after creating the Flask 'app' context above so that
# handler.py can import it `from flask import current_app as app`.
from function import handler


# distutils.util.strtobool() can throw an exception
def is_true(val):
    return len(val) > 0 and val.lower() == "true" or val == "1"

@app.before_request
def fix_transfer_encoding():
    """
    Sets the "wsgi.input_terminated" environment flag, thus enabling
    Werkzeug to pass chunked requests as streams.  The gunicorn server
    should set this, but it's not yet been implemented.
    """

    transfer_encoding = request.headers.get("Transfer-Encoding", None)
    if transfer_encoding == u"chunked":
        request.environ["wsgi.input_terminated"] = True

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def call_handler(path):
    raw_body = os.getenv("RAW_BODY", "false")

    as_text = True

    if is_true(raw_body):
        as_text = False

    ret = handler.handle(request.get_data(as_text=as_text))
    return ret

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
