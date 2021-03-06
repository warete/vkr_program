from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import json
import os
import shutil
from sklearn.metrics import accuracy_score

from vkr import Vkr
from utils import CustomFlask, allowed_file, clear_pickle_files

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
VkrInstance.check_or_copy_data_file()
VkrInstance.init()


@app.route('/')
def index():
    return render_template('index.html', debug=app.debug, host=request.host_url,
                           filepath=app.config['DATA_DIR'] + VkrInstance.data_file)


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
        if VkrInstance.need_fit_model(post_data.get('method'), post_data.get('testPercent')):
            response['status'] = 'warning'
            response['message'] = 'Нужно сначала обучить'
        else:
            clf = VkrInstance.get_fitted_model(post_data.get('method'), post_data.get('testPercent'))
            yPred = clf.predict(VkrInstance.xTest)
            accuracy = accuracy_score(VkrInstance.yTest, yPred)
            response['status'] = 'success'
            response['metrics'] = {
                'accuracy': accuracy,
                'sensitivity': VkrInstance.calculate_sensitivity(yPred) * 100,
                'specificity': VkrInstance.calculate_specificity(yPred) * 100
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


@app.route('/methods/', methods=['POST'])
def methods():
    formatted_methods = {}
    i = 0
    for key in VkrInstance.methods:
        formatted_methods[i] = {
            'name': VkrInstance.methods[key]['name'],
            'code': key,
            'canPredict': True,
            'metrics': {
                'sensitivity': 0,
                'specificity': 0,
                'accuracy': []
            }
        }
        i += 1
    response = {
        'status': 'success',
        'methods': formatted_methods
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
            diagnose_class, predicted_point, accuracy = VkrInstance.get_diagnose(post_data.get('method'),
                                                                       post_data.get('testPercent'),
                                                                       post_data.get('patientData'))

            response['status'] = 'success'
            response['result'] = {
                'class': str(diagnose_class),
                'point': str(predicted_point),
                'accuracy': accuracy
            }

    return jsonify(response)


@app.route('/upload_data/', methods=['POST'])
def upload_data():
    file = request.files['file']
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['DATA_DIR'], VkrInstance.data_file)
        # бэкап старого файла
        shutil.copyfile(os.path.join(app.config['DATA_DIR'], VkrInstance.data_file),
                  os.path.join(app.config['DATA_DIR'], 'old_' + VkrInstance.data_file))
        file.save(file_path)

        # Удаляем старые pickle-файлы
        clear_pickle_files(app.config['DATA_DIR'])
        # Перечитаем файл с данными
        # VkrInstance.init()
        print("lol")
        return jsonify({
            'status': 'success',
            'result': {
                'file_path': file_path
            }
        })
    else:
        return jsonify({
            'status': 'error',
            'result': {
                'message': 'Неподходящий тип файла'
            }
        })


if __name__ == '__main__':
    app.run(debug=app.debug)
