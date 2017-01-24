"""
Flask blueprint implementing RESTful web interface
used to upload various network parameters.
"""
import logging
import json

from flask import Blueprint, request, Response, abort
from altoserver import nm

netupload = Blueprint('netupload', __name__)

@netupload.route('/<device_name>/adapter_stats', methods=['GET', 'POST'])
def upload_device_adapter_stats(device_name):
    """Process the incomming request with adapter stats"""

    # Process GET for easier debugging
    if request.method == 'GET':
        # Return error response
        resp = Response(
            response=json.dumps({'error':'GET not allowed'}),
            mimetype='application/json'
        )
        resp.status_code = 405
        return resp

    if not request.is_json:
        abort(400)

    return 'X'

@netupload.route('/<device_name>/rtable', methods=['GET', 'POST'])
def upload_device_routing_table(device_name):
    """Process the incomming request with routing table data"""

    # Process GET for easier debugging
    if request.method == 'GET':
        # Return error response
        resp = Response(
            response=json.dumps({'error':'GET not allowed'}),
            mimetype='application/json'
        )
        resp.status_code = 405
        return resp

    # Process post request
    if not request.is_json:
        abort(400)

    return 'Y'

@netupload.route('/<device_name>/quagga_rt', methods=['GET', 'POST'])
def upload_quagga_routing_table(device_name):
    """Process the incomming request with quagga routing table"""

    # Process GET for easier debugging
    if request.method == 'GET':
        # Return error response
        resp = Response(
            response=json.dumps({'error':'GET not allowed'}),
            mimetype='application/json'
        )
        resp.status_code = 405
        return resp

    if not request.is_json:
        abort(400)

    print(request.json)

    return 'X'
