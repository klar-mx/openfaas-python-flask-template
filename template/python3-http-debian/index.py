#!/usr/bin/env python
from flask import Flask, request, jsonify
from waitress import serve
import os


app = Flask(os.environ.get('FLASK_APP', __name__.split('.')[0]))
app.app_context().push()

# Import this after creating the Flask 'app' context above so that
# handler.py can import it `from flask import current_app as app`.
from function import handler


class Event:
    def __init__(self):
        self.body = request.get_data()
        self.headers = request.headers
        self.method = request.method
        self.query = request.args
        self.path = request.path

class Context:
    def __init__(self):
        self.hostname = os.getenv('HOSTNAME', 'localhost')

def format_status_code(res):
    if 'statusCode' in res:
        return res['statusCode']

    return 200

def format_body(res, content_type):
    if content_type == 'application/octet-stream':
        return res['body']

    if 'body' not in res:
        return ""
    elif type(res['body']) == dict:
        return jsonify(res['body'])
    else:
        return str(res['body'])

def format_headers(res):
    if 'headers' not in res:
        return []
    elif type(res['headers']) == dict:
        headers = []
        for key in res['headers'].keys():
            header_tuple = (key, res['headers'][key])
            headers.append(header_tuple)
        return headers

    return res['headers']

def get_content_type(res):
    content_type = ""
    if 'headers' in res:
        content_type = res['headers'].get('Content-type', '')
    return content_type

def format_response(res):
    if res == None:
        return ('', 200)

    statusCode = format_status_code(res)
    content_type = get_content_type(res)
    body = format_body(res, content_type)

    headers = format_headers(res)

    return (body, statusCode, headers)

@app.route('/', defaults={'path': ''}, methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'PUT', 'POST', 'PATCH', 'DELETE'])
def call_handler(path):
    event = Event()
    context = Context()

    response_data = handler.handle(event, context)

    res = format_response(response_data)
    return res

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000, server_name=os.environ.get('FLASK_APP', 'faas-fn/python3-http-debian'), clear_untrusted_proxy_headers=False)

