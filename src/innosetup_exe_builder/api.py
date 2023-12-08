import subprocess
from http.client import BAD_REQUEST, OK

from flask import Flask, Blueprint, json,  jsonify, request
from werkzeug.exceptions import HTTPException

from innosetup_exe_builder.helpers import check_invalid_params

api = Blueprint("api", __name__)

@api.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@api.route("/compile", methods=["POST"])
def compile_exe():
    """
    Given a path and a file name, runs command to compile the executable.
    """
    path = request.form.get("path")
    file_name = request.form.get("file_name")
    if not file_name:
        file_name = "memor-i_config.iss"
    if check_invalid_params(path, file_name):
        return jsonify({"error": "Invalid path or file name"}), BAD_REQUEST

    command = (
        f'docker run --rm -i -v "{path}:/work" amake/innosetup:innosetup6 "{file_name}"'
    )
    subprocess.run(command,
                   shell=True,
                   capture_output=True,
                   text=True
                   )  # NOQA: S602

    return jsonify({"result": 1}), OK
