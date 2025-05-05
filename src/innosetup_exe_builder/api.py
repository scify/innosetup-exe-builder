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
    Given a path and a file name, runs command to compile the executable.
    Logs the steps into a log file located at the top directory of the project.
    """
    path = request.form.get("path")
    file_name = request.form.get("file_name")
    if not file_name:
        file_name = "memor-i_config.iss"
    if check_invalid_params(path, file_name):
        return jsonify({"error": "Invalid path or file name"}), BAD_REQUEST

    # Define the log file path at the top directory of the project
    top_dir = os.path.dirname(os.path.abspath(__file__))  # Get current file's directory
    log_file_path = os.path.join(top_dir, "../../compile_log.txt")  # Navigate to the top directory

    command = (
        f'docker run --rm -i -v "{path}:/work" amake/innosetup:innosetup6 "{file_name}"'
    )
    with open(log_file_path, "a") as log_file:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )  # NOQA: S602

        # Write the output and errors to the log file
        log_file.write("Command executed:\n")
        log_file.write(command + "\n")
        log_file.write("Standard Output:\n")
        log_file.write(result.stdout + "\n")
        log_file.write("Standard Error:\n")
        log_file.write(result.stderr + "\n")
        log_file.write("Exit Code:\n")
        log_file.write(f"{result.returncode}\n\n")

    if result.returncode != 0:
        return jsonify({"error": "Compilation failed. Check the log for details"}), BAD_REQUEST

    return jsonify({"result": 1}), OK
