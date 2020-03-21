from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

import pandas as pd
import pickle
import os.path

from sklearn.svm import SVC
from sklearn import neighbors
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import BaggingClassifier
from sklearn.linear_model import SGDClassifier


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
app.config['DATA_DIR'] = 'data/'

# enable CORS
CORS(app)

data = pd.read_csv(app.config['DATA_DIR'] + 'data.csv',
                   delimiter=',',
                   names=['0ртм', '1ртм', '2ртм', '3ртм', '4ртм', '5ртм', '6ртм', '7ртм', '8ртм',
                          '0ик', '1ик', '2ик', '3ик', '4ик', '5ик', '6ик', '7ик', '8ик', 'target', 'position'])

xTrain, xTest, yTrain, yTest = train_test_split(
    data[['0ртм', '1ртм', '2ртм', '3ртм', '4ртм', '5ртм', '6ртм', '7ртм', '8ртм',
          '0ик', '1ик', '2ик', '3ик', '4ик', '5ик', '6ик', '7ик', '8ик']],
    data.target,
    test_size=0.25,
    random_state=0
)

methods = {
    'svm': SVC(gamma='scale'),
    'knn': neighbors.KNeighborsClassifier(5, weights='uniform'),
    'bagging': BaggingClassifier(SVC(gamma='scale'), max_samples=0.5, max_features=0.5),
    'sgd': SGDClassifier()
}


def get_pickled_file_name(model_name):
    return app.config['DATA_DIR'] + 'model_' + model_name + '_fitted.pickle'


def need_fit_model(name):
    return os.path.isfile(get_pickled_file_name(name)) == False


def get_fitted_model(name, need_fit=False):
    if need_fit_model(name) or need_fit:
        methods[name] = methods[name].fit(xTrain, yTrain)
        with open(get_pickled_file_name(name), 'wb') as f:
            pickle.dump(methods[name], f)
    else:
        with open(get_pickled_file_name(name), 'rb') as f:
            methods[name] = pickle.load(f)

    return methods[name]


@app.route('/')
def index():
    return render_template('index.html', debug=app.debug, host=request.host_url)


@app.route('/train/', methods=['POST'])
def train():
    post_data = request.get_json()
    response = {
        'status': 'error',
    }
    if methods[post_data.get('method')]:
        clf = get_fitted_model(post_data.get('method'), True)
        response['status'] = 'success'
        response['method'] = {
            'code': post_data.get('method'),
            'id': post_data.get('methodId')
        }
    return jsonify(response)


@app.route('/predict/', methods=['POST'])
def predict():
    post_data = request.get_json()
    response = {
        'status': 'error',
    }

    if methods[post_data.get('method')]:
        if need_fit_model(post_data.get('method')):
            response['status'] = 'warning'
            response['message'] = 'Нужно сначала обучить'
        else:
            clf = get_fitted_model(post_data.get('method'))
            yPred = clf.predict(xTest)
            accuracy = accuracy_score(yTest, yPred)
            response['status'] = 'success'
            response['metrics'] = {
                'accuracy': accuracy
            }
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=app.debug)
