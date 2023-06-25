#!/usr/bin/env python3
from flask import Flask, make_response, request, redirect
from lib import State
from utils import map_action
import os
import requests
import json

app = Flask(__name__)

EMULATOR_PORT = int(os.getenv('EMULATOR_PORT', 8888))

state = State('/dump.json')


@app.route('/execute', methods=['POST'])
def execute():
    global state
    try:
        data = request.get_json()
        el = data['element'].split('.')
        action = data['action']
        args = data['args']
        assert type(args) == list
        element = state
        for e in el:
            element = element.get_elements().get(e)
        func = map_action(element, action)

        result = func(*args)
        return make_response({'status': 'ok', 'result': result}, 200)
    except Exception as e:
        print(e, flush=True)
        return make_response({'error': True}, 500)


@app.route('/reset_state', methods=['POST'])
def reset():
    global state
    try:
        state = State('/dump.json')
        return make_response({'status': 'ok'}, 200)
    except Exception as e:
        print(e, flush=True)
        return make_response({'error': True}, 500)


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'


@app.route('/state', methods=['GET'])
def get_state():
    return make_response(state.export_(), 200)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=EMULATOR_PORT)
