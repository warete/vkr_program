from flask import Flask
from pathlib import Path

ALLOWED_EXTENSIONS = set(['csv'])


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def clear_pickle_files(data_dir):
    path = Path(data_dir)
    for f in path.glob("*.pickle"):
        if not str(f).endswith("F"):
            f.unlink()