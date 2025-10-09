#!/usr/bin/env python3
import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path
from typing import Optional

try:
    from flask import Flask, render_template, request, jsonify, Response
except Exception:
    # Deps not installed yet; app won't run until Flask is installed
    Flask = None

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
LOGS_DIR = ROOT / 'webui' / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

_state = {
    'proc': None,
    'log_path': str(LOGS_DIR / 'run.log'),
    'running': False,
}

app = Flask(__name__, template_folder=str(ROOT / 'webui' / 'templates'), static_folder=str(ROOT / 'webui' / 'static')) if Flask else None


def _start_process(args: list, log_path: str):
    with open(log_path, 'w', encoding='utf-8') as log:
        proc = subprocess.Popen(args, cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT, text=True)
    return proc


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def api_start():
    if _state['running']:
        return jsonify({'ok': False, 'error': 'Already running'}), 409
    data = request.get_json(force=True)
    cities = data.get('cities') or []
    mode = data.get('mode') or 'full'
    headless = bool(data.get('headless', False))
    pages = int(data.get('pages', 50))
    include_pdp = bool(data.get('include_pdp', True))

    # For v1, call the existing validation runner (ignores some params)
    args = [sys.executable, str(TOOLS / 'run_multi_city_validation.py')]

    _state['proc'] = _start_process(args, _state['log_path'])
    _state['running'] = True
    return jsonify({'ok': True})


@app.route('/api/stop', methods=['POST'])
def api_stop():
    if not _state['running'] or not _state['proc']:
        return jsonify({'ok': False, 'error': 'Not running'}), 400
    _state['proc'].terminate()
    _state['proc'] = None
    _state['running'] = False
    return jsonify({'ok': True})


@app.route('/api/status')
def api_status():
    running = _state['running'] and _state['proc'] and (_state['proc'].poll() is None)
    if _state['running'] and not running:
        _state['running'] = False
    return jsonify({'running': running})


@app.route('/api/logs')
def api_logs():
    def stream():
        path = Path(_state['log_path'])
        path.touch(exist_ok=True)
        with path.open('r', encoding='utf-8', errors='ignore') as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                yield f"data: {line.rstrip()}\n\n"
    return Response(stream(), mimetype='text/event-stream')


if __name__ == '__main__':
    if not Flask:
        print('Flask is not installed. Please install it (e.g., pip install flask) to run the web UI.')
        sys.exit(1)
    app.run(host='127.0.0.1', port=8080, debug=True)

