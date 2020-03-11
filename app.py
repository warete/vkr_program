from flask import Flask, jsonify, render_template
from flask_cors import CORS

# instantiate the app
app = Flask(__name__, static_folder="assets")
app.config.from_object(__name__)
app.config['DEBUG'] = True

# enable CORS
CORS(app)

@app.route('/')
def index():
    return render_template('index.html', debug=app.debug)

if __name__ == '__main__':
    app.run(debug=app.debug)