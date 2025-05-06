import subprocess
import os
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

import os  # Import os to determine the top directory dynamically

@api.route("/compile", methods=["POST"])
def compile_exe():
    """
    Given a full path to a .iss file, runs command to compile the executable.
    The resulting .exe will be stored in the 'Output' subdirectory of the .iss file's directory.
    Logs the steps into a log file located at the top directory of the project.
    """
    iss_path = request.form.get("iss_path")
    launch4j_config_path = request.form.get("launch4j_config_path")
    if not iss_path or not os.path.isfile(iss_path):
        return jsonify({"error": "Invalid or missing .iss file path"}), BAD_REQUEST
    if not launch4j_config_path or not os.path.isfile(launch4j_config_path):
        return jsonify({"error": "Invalid or missing Launch4j config path"}), BAD_REQUEST

    # Ensure Windows (CRLF) line endings for the .iss file
    with open(iss_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(iss_path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(content)

    # --- Step 1: Run Launch4j ---
    config_dir = os.path.dirname(launch4j_config_path)
    config_file = os.path.basename(launch4j_config_path)
    launch4j_cmd = (
        f'docker run --rm -v "{config_dir}:/work" progap/launch4j-build-image launch4j /work/{config_file}'
    )
    launch4j_result = subprocess.run(
        launch4j_cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    if launch4j_result.returncode != 0:
        return jsonify({
            "error": "Launch4j failed",
            "stdout": launch4j_result.stdout,
            "stderr": launch4j_result.stderr
        }), BAD_REQUEST

    # --- Step 2: Run Inno Setup as before ---
    iss_dir = os.path.dirname(iss_path)
    iss_file = os.path.basename(iss_path)
    command = (
        f'docker run --rm -i -v "{iss_dir}:/work" amake/innosetup:innosetup6 "{iss_file}"'
    )
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return jsonify({
            "error": "Inno Setup compilation failed",
            "stdout": result.stdout,
            "stderr": result.stderr
        }), BAD_REQUEST

    return jsonify({"result": 1, "output_dir": os.path.join(iss_dir, "Output")}), OK
