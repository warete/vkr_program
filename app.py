from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import json

from vkr import Vkr

from sklearn.svm import SVC
from sklearn import neighbors
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

# Vkr instance
VkrInstance = Vkr()
VkrInstance.set_data_dir(dir=app.config['DATA_DIR'])
VkrInstance.data_file = 'data.csv'
VkrInstance.xTrain, VkrInstance.xTest, VkrInstance.yTrain, VkrInstance.yTest = VkrInstance.get_train_test_data(0.25)
VkrInstance.set_methods({
    'svm': SVC(gamma='scale'),
    'knn': neighbors.KNeighborsClassifier(5, weights='uniform'),
    'bagging': BaggingClassifier(SVC(gamma='scale'), max_samples=0.5, max_features=0.5),
    'sgd': SGDClassifier()
})


@app.route('/')
def index():
    return render_template('index.html', debug=app.debug, host=request.host_url)


@app.route('/train/', methods=['POST'])
def train():
    post_data = json.loads(request.get_data())
    response = {
        'status': 'error',
    }
    if post_data.get('method') in VkrInstance.methods:
        clf = VkrInstance.get_fitted_model(post_data.get('method'), post_data.get('testPercent'), True)
        response['status'] = 'success'
        response['method'] = {
            'code': post_data.get('method'),
            'id': post_data.get('methodId')
        }
    return jsonify(response)


@app.route('/predict/', methods=['POST'])
def predict():
    post_data = json.loads(request.get_data())
    response = {
        'status': 'error',
    }

    if post_data.get('method') in VkrInstance.methods:
        if VkrInstance.need_fit_model(post_data.get('method')):
            response['status'] = 'warning'
            response['message'] = 'Нужно сначала обучить'
        else:
            clf = VkrInstance.get_fitted_model(post_data.get('method'), post_data.get('testPercent'))
            yPred = clf.predict(VkrInstance.xTest)
            accuracy = accuracy_score(VkrInstance.yTest, yPred)
            response['status'] = 'success'
            response['metrics'] = {
                'accuracy': accuracy,
                'sensitivity': VkrInstance.calculate_sensitivity(yPred),
                'specificity': VkrInstance.calculate_specificity(yPred)
            }
    return jsonify(response)


@app.route('/static_metrics/', methods=['POST'])
def static_metrics():
    try:
        post_data = json.loads(request.get_data())
        response = {
            'status': 'success',
            'metrics': {
                'frequencyTemperature': VkrInstance.get_temp_freq(),
                'frequencyTumor': VkrInstance.get_tumor_freq()
            }
        }
    except Exception as e:
        response = {
            'status': 'error',
            'message': e.message
        }

    return jsonify(response)


@app.route('/diagnose/', methods=['POST'])
def diagnose():
    post_data = json.loads(request.get_data())
    response = {
        'status': 'error',
    }

    if post_data.get('method') in VkrInstance.methods:
        if VkrInstance.need_fit_model(post_data.get('method')):
            response['status'] = 'warning'
            response['message'] = 'Нужно сначала обучить'
        else:
            clf = VkrInstance.get_fitted_model(post_data.get('method'), post_data.get('testPercent'))
            xPredict = []
            for i in post_data.get('patientData')['rt']:
                xPredict.append(i)
            for i in post_data.get('patientData')['rt']:
                xPredict.append(i)
            yPred = clf.predict([xPredict])
            response['status'] = 'success'
            response['result'] = {
                'class': str(yPred[0])
            }
    return jsonify(response)

@app.route('/test/')
def test():
    from sklearn.model_selection import train_test_split
    from sklearn.model_selection import GridSearchCV
    data = VkrInstance.data[VkrInstance.data.position != 10]
    xTrain, xTest, yTrain, yTest = train_test_split(
            data[VkrInstance.temp_columns],
            data.position,
            test_size=0.25,
            random_state=0
        )
    yPred = SVC(gamma='scale').fit(xTrain, yTrain).predict(xTest)
    print(yPred)
    print(accuracy_score(yTest, yPred))
    return ''


if __name__ == '__main__':
    app.run(debug=app.debug)
