from flask import Flask, jsonify, render_template
from flask_cors import CORS

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        variable_start_string='%%',  # Default is '{{', I'm changing this because Vue.js uses '{{' / '}}'
        variable_end_string='%%',
    ))

# instantiate the app
app = CustomFlask(__name__, static_folder="assets")
app.config.from_object(__name__)
app.config['DEBUG'] = True

# enable CORS
CORS(app)

@app.route('/')
def index():
    return render_template('index.html', debug=app.debug)

if __name__ == '__main__':
    app.run(debug=app.debug)