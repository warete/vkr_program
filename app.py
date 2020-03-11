from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

import pandas as pd
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

# enable CORS
CORS(app)


data = pd.read_csv('data/data.csv',
                   delimiter=',',
                   names=['0ртм', '1ртм', '2ртм', '3ртм', '4ртм', '5ртм', '6ртм', '7ртм', '8ртм',
                          '0ик', '1ик', '2ик', '3ик', '4ик', '5ик', '6ик', '7ик', '8ик', 'target', 'position'])

xTrain, xTest, yTrain, yTest = train_test_split(
    data[['0ртм', '1ртм', '2ртм', '3ртм', '4ртм', '5ртм', '6ртм', '7ртм', '8ртм',
                          '0ик', '1ик', '2ик', '3ик', '4ик', '5ик', '6ик', '7ик', '8ик']],
    data.target,
    test_size = 0.25,
    random_state = 0
)

methods = {
    'svm': SVC(gamma='scale').fit(xTrain, yTrain),
    'knn': neighbors.KNeighborsClassifier(5, weights='uniform').fit(xTrain, yTrain),
    'bagging': BaggingClassifier(SVC(gamma='scale'), max_samples=0.5, max_features=0.5).fit(xTrain, yTrain),
    'sgd': SGDClassifier().fit(xTrain, yTrain)
}

@app.route('/')
def index():
    return render_template('index.html', debug=app.debug)


@app.route('/predict/', methods=['POST'])
def train():
    post_data = request.get_json()
    response = {
        'status': 'error',
    }
    if methods[post_data.get('method')]:
        yPred = methods[post_data.get('method')].predict(xTest)
        accuracy = accuracy_score(yTest, yPred)
        response['status'] = 'success'
        response['metrics'] = {
            'accuracy': accuracy
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=app.debug)