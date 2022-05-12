import functions_framework
import traceback
from typing import Callable
from flask import *

from pprint import pprint
from markupsafe import escape

from v2.types import is_fbe_format

from v2.to_program import to_program as to_program_v2

support_v2_versions = [
    "2.0.0",
    "2.1.0",
]


def cors(handler: Callable[[Request], Response]):
    # CORS対応
    def ans(request):
        if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600'
            }
            return ('', 204, headers)
        else:
            res = handler(request)
            res.headers.set("Access-Control-Allow-Origin", "*")
            print("response body", res.get_json())
            return res
    return ans


@functions_framework.http
@cors
def fbeToProgram(request: Request) -> Response:
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """

    print(f"\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {request}")
    request_json = request.get_json()
    if request_json is None:
        res = jsonify({
            "msg": "error",
            "error": "invalid request body"
        })
        print(request_json)
        return res

    # 本文

    # バリデーション
    try:
        if not is_fbe_format(request_json["fbe"]):
            res = jsonify({
                "msg": "error",
                "error": f"{request_json['fbe']} is not fbe format"
            })
            # res.headers.set("Access-Control-Allow-Origin", "*")
            return res
        # if request_json["fbe"]["version"] == "2.0.0":
        if request_json["fbe"]["version"] in support_v2_versions:
            ans = to_program_v2(request_json["fbe"], request_json["target"])
            res = jsonify(ans)
            # res.headers.set("Access-Control-Allow-Origin", "*")
            return res
        else:
            print(f"invalid version : {request_json['fbe']['version']}")
            body = {}
            res = jsonify(body)
            return res
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        res = jsonify({
            "error": e.__str__(),
            "details": "",
        })
        res.status_code = 500
        return res


print("server start !!!!!")
