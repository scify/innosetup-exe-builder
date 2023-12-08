from pathlib import Path


def check_invalid_params(path, file_name):
    """
    Checks if the path and file name are valid.
    """

    full_path = Path(path) / file_name

    if not full_path.exists() or not full_path.is_file():
        return True

    return False
