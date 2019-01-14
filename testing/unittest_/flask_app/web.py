#!/usr/bin/env python

import logging
import requests

from flask import Flask, render_template
app = Flask(__name__)
app.config['debug'] = True

logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def hello_world():
    return render_template('layout.html')


@app.route('/foo')
def foo_endpoint():
    return '{"data":"foo"}'


@app.route('/bar')
def bar_endpoint():
    return '{"data":"bar"}'


@app.route('/baz')
def baz_endpoint():
    return '{"data":"baz"}'


if __name__ == '__main__':
    app.run('0.0.0.0')
