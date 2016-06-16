#!/usr/bin/env python

import logging
import requests

from flask import Flask, render_template
app = Flask(__name__)
app.config['debug'] = True

logging.basicConfig(filename='/shared/web.log', level=logging.DEBUG)


def get_addresses():
    d = {}
    for line in open('/shared/addresses').readlines():
        host, addr = line.strip().split('=')
        d[host] = addr
    return d


@app.route('/')
def hello_world():
    return render_template('layout.html')


@app.route('/start')
def start():
    addrs = get_addresses()
    r = requests.get('http://%s:5000/start' % addrs['worker'])
    assert r.status_code == 200, r.text
    return r.text


@app.route('/start-debug')
def start_with_debug():
    addrs = get_addresses()
    r = requests.get('http://%s:5000/start-debug' % addrs['worker'])
    assert r.status_code == 200, r.text
    return r.text


@app.route('/images/<path:path>')
def show_image(path):
    return open('static/' + path).read()


@app.route('/jobsdata')
def get_jobs():
    addrs = get_addresses()
    r = requests.get('http://%s:5000/all' % addrs['worker'])
    assert r.status_code == 200, r.text
    return '{"data":' + r.text + '}'

@app.route('/results')
def get_results():
    addrs = get_addresses()
    r = requests.get('http://%s:5000/results' % addrs['worker'])
    assert r.status_code == 200, r.text
    return '{"data":' + r.text + '}'

@app.route('/clear')
def clear_everything():
    addrs = get_addresses()
    r = requests.get('http://%s:5000/clear' % addrs['worker'])
    assert r.status_code == 200, r.text
    return ''

if __name__ == '__main__':
    app.run('0.0.0.0')
