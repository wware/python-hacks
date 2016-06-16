#!/usr/bin/env python

import json
import logging
from werkzeug.exceptions import abort
from flask import Flask, request, render_template

# Don't enable logging, there is a 1-second polling loop in the JavaScript, so
# you'll fill up the file system unnecessarily.
# logging.basicConfig(filename='/var/log/rdb-listener.log', level=logging.INFO)

app = Flask(__name__)
logs = []
rdbid = 0

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/images/<path:path>')
def show_image(path):
    return open('static/' + path).read()

def jtable(x):
    return json.dumps(
        dict(data=x),
        sort_keys=True,
        indent=4, separators=(',', ': ')
    )

@app.route('/get_logs')
def get_logs():
    return jtable(logs)


@app.route('/log', methods=['POST'])
def post_log():
    log = {
        'ipaddr': request.form['ipaddr'],
        'levelname': request.form['levelname'],
        'pathname': request.form['pathname'],
        'lineno': request.form['lineno'],
        'funcName': request.form['funcName'],
        'exc_info': request.form['exc_info'],
        'msg': request.form['msg'],
        'created': request.form['created']
    }
    logs.append(log)
    return ''

rdb_sessions = []

@app.route('/rdb', methods=['POST'])
def post_rdb():
    global rdbid
    rdb_sessions.append((rdbid, request.form['ipaddr'], request.form['port']))
    rdbid += 1
    return ''

@app.route('/check-rdb', methods=['GET'])
def get_rdb():
    sessions = [
        {'id': id, 'ipaddr': ipaddr, 'port': port} for id, ipaddr, port in rdb_sessions
    ]
    return render_template('rdblist.html', rdblist=sessions)

@app.route('/rdb-done/<n>')
def remove_rdb(n):
    global rdb_sessions
    rdb_sessions = filter(lambda session: session[0] != int(n), rdb_sessions)
    return ''

if __name__ == '__main__':
    app.run('0.0.0.0')
