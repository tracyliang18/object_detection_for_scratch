#!/usr/bin/env mdl
import os
import time
import json
import select
import traceback
from multiprocessing import Process, Pipe

from utils.logconf import get_logger

import gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, request, render_template, abort, send_file

logger = get_logger(__name__)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

HOSTNAME = os.environ.get('HOSTNAME', '127.0.0.1')

def log_important_msg(msg, *, padding=3):
    msg_len = len(msg)
    width = msg_len + padding * 2 + 2
    print('#' * width)
    print('#' + ' ' * (width - 2) + '#')
    print('#' + ' ' * padding + msg + ' ' * padding + '#')
    print('#' + ' ' * (width - 2) + '#')
    print('#' * width)


def hint_url(url, port):
    log_important_msg(
        'The server is running at: {}'.format(url))

def get_domain_name():
    return HOSTNAME


def _set_server(conn, name='webcv2', port=7788):
    package = None
    package_alive = False

    ws_url = 'ws://{}:{}/stream'.format(get_domain_name(), port)
    app = Flask(name)
    app.root_path = BASE_DIR

    @app.route('/')
    def index():
        return render_template('index.html', ws_url=ws_url, title=name)

    @app.route('/src/<path:path>')
    def serve_src(path):
        return send_file(os.path.join(BASE_DIR, 'static', path))

    @app.route('/stream')
    def stream():
        def poll_ws(ws, delay):
            return len(select.select([ws.stream.handler.rfile], [], [], delay / 1000.)[0]) > 0

        if request.environ.get('wsgi.websocket'):
            ws = request.environ['wsgi.websocket']
            if ws is None:
                abort(404)
            else:
                should_send = True
                while not ws.closed:
                    global package
                    global package_alive
                    if conn.poll():
                        package = conn.recv()
                        package_alive = True
                        should_send = True
                    if not should_send:
                        continue
                    should_send = False
                    if package is None:
                        ws.send(None)
                    else:
                        delay, info_lst = package
                        ws.send(json.dumps((time.time(), package_alive, delay, info_lst)))
                        if package_alive:
                            if delay <= 0 or poll_ws(ws, delay):
                                message = ws.receive()
                                if ws.closed or message is None:
                                    break
                                try:
                                    if isinstance(message, bytes):
                                        message = message.decode('utf8')
                                    message = int(message)
                                except Exception:
                                    traceback.print_exc()
                                    message = -1
                            else:
                                message = -1
                            conn.send(message)
                            package_alive = False
        return ""

    http_server = WSGIServer(('', port), app, handler_class=WebSocketHandler)
    hint_url('http://{}:{}'.format(get_domain_name(), port), port)
    http_server.serve_forever()


def get_server(name='webcv2', port=7788):
    conn_server, conn_factory = Pipe()
    p_server = Process(
        target=_set_server,
        args=(conn_server,),
        kwargs=dict(
            name=name, port=port,
        ),
    )
    p_server.daemon = True
    p_server.start()
    return p_server, conn_factory

# vim: ts=4 sts=4 sw=4 expandtab
