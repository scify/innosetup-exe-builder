from http.client import BAD_REQUEST, OK
from flask import Blueprint, jsonify, request
from memori_exe_builder.helpers import check_invalid_params
import subprocess



api = Blueprint('api', __name__)

@api.route('/compile', methods=['POST'])
def compile_exe():
    """ 
    Given a path and a file name, runs command to compile the executable.
    """
    path = request.form.get('path')
    file_name = request.form.get('file_name')

    if check_invalid_params(path, file_name):
        return jsonify({'error': 'Invalid path or file name'}), BAD_REQUEST
    
    command = f'docker run --rm -i -v "{path}:/work" amake/innosetup:innosetup6 "{file_name}"'
    subprocess.run(command, shell=True) # NOQA: S602
    
    return jsonify({"result": 1}), OK


