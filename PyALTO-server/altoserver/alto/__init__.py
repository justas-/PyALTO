"""
PyALTO, a Python3 implementation of Application Layer Traffic Optimization protocol
Copyright (C) 2016,2017  J. Poderys, Technical University of Denmark

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
ALTO protocol RESTful API.
Functions here should be only a shim between Flask and ALTO
implementation in AltoServer class
"""
import json
import logging

from flask import Blueprint, Response, request, abort

from .altoserver import AltoServer

from .addresstypes import *
from .costproviders import *
from .propertyproviders import *

alto_server = AltoServer()
alto_server.register_address_parsers([
    ipaddrparser.IPAddrParser()
])
alto_server.register_cost_providers([
    ospfcostprovider.OSPFCostProvider(),
    routehopscostprovider.RouteHopsCostProvider(),
    pathhopscostprovider.PathHopsCostProvider(),
    pathloadcostprovider.PathLoadCostProvider()
])
alto_server.register_property_providers([
    pidpropertyprovider.PIDPropertyProvider(),
    hostnamepropertyprovider.HostnamePropertyProvider(),
])

alto = Blueprint('alto', __name__)

@alto.route('/networkmap')
def get_network_map():
    """Get ALTO network map """ 

    # TODO: Any request validity checking here

    # Get the map
    try:
        resp = alto_server.get_network_map()
    except Exception as exc:
        logging.exception('Exc in networkmap', exc_info = exc)
        abort(500)
        
    # Return properly structured response
    return Response(
        json.dumps(resp),
        mimetype='application/alto-networkmap+json'
    )

@alto.route('/endpointprop/lookup', methods=['POST'])
def get_endpoint_properties():
    """Return endpoint properties [RFC7285] p 11.4.1"""

    # Do any other request checks

    # Drop early if not json
    if not request.is_json:
        abort(400)

    req_data = request.json

    # Ensure that required keys are there
    if 'properties' not in req_data:
        abort(400)

    if 'endpoints' not in req_data:
        abort(400)

    # Request data. Do not try to parse requested
    # data here. This is only a shim layer
    try:
        resp = alto_server.get_endpoint_properties(
            req_data['properties'],
            req_data['endpoints']
        )
    except Exception as exc:
        logging.exception('Exc in endpoint properties', exc_info = exc)
        abort(500)

    # Return if successfull
    return Response(
        json.dumps(resp),
        mimetype='application/alto-endpointprop+json'
    )

@alto.route('/endpointcost/lookup', methods=['POST'])
def get_endpoint_cost():
    """Return endpoint costs [RFC7285] p 11.5.1"""
    # Do any other request checks

    # Drop early if not json
    if not request.is_json:
        abort(400)

    req_data = request.json

    # Ensure that required keys and data are there
    if 'cost-type' not in req_data:
        abort(400)

    if 'cost-mode' not in req_data['cost-type']:
        abort(400)

    if 'cost-metric' not in req_data['cost-type']:
        abort(400)

    if 'endpoints' not in req_data:
        abort(400)

    if 'srcs' not in req_data['endpoints']:
        abort(400)

    if 'dsts' not in req_data['endpoints']:
        abort(400)

    if not any(req_data['endpoints']['srcs']):
        abort(400)

    if not any(req_data['endpoints']['dsts']):
        abort(400)

    # Request data. Do not try to parse requested
    # data here. This is only a shim layer

    try:
        costmap = alto_server.get_endpoint_costs(
            req_data['cost-type'],
            req_data['endpoints']
        )
    except Exception as exc:
        logging.exception('Exc in endpoint costs', exc_info = exc)
        abort(500)

    # Return if successfull
    return Response(
        json.dumps(costmap),
        mimetype='application/alto-endpointcost+json'
    )
