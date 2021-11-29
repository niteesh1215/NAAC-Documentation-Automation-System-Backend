from flask import jsonify
from flask.wrappers import Response


def get_success_response(data: any, status_code=200) -> Response:
    resp = jsonify({
        'status': 'success',
        'data': data
    })
    resp.status_code = status_code 
    return resp


def get_failed_response(data: any, status_code=200) -> Response:
    resp = jsonify({
        'status': 'failed',
        'data': data
    })
    resp.status_code = status_code
    return resp
