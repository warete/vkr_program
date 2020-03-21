from sklearn.model_selection import train_test_split
import pandas as pd
import pickle
import os.path


class Vkr:
    data_dir = 'data/'
    data_file = 'data.cv'

    methods = {}

    xTrain, yTrain, xTest, yTest = [], [], [], []

    def set_data_dir(self, dir):
        self.data_dir = dir

    def set_methods(self, methods):
        self.methods = methods

    def get_train_test_data(self, test_sizе):
        data = pd.read_csv(self.data_dir + self.data_file,
                           delimiter=',',
                           names=['0ртм', '1ртм', '2ртм', '3ртм', '4ртм', '5ртм', '6ртм', '7ртм', '8ртм',
                                  '0ик', '1ик', '2ик', '3ик', '4ик', '5ик', '6ик', '7ик', '8ик', 'target', 'position'])

        return train_test_split(
            data[['0ртм', '1ртм', '2ртм', '3ртм', '4ртм', '5ртм', '6ртм', '7ртм', '8ртм',
                  '0ик', '1ик', '2ик', '3ик', '4ик', '5ик', '6ик', '7ик', '8ик']],
            data.target,
            test_size=test_sizе,
            random_state=0
        )

    def get_pickled_file_name(self, model_name):
        return self.data_dir + 'model_' + model_name + '_fitted.pickle'

    def need_fit_model(self, name, test_percent=25):
        return os.path.isfile(self.get_pickled_file_name(name + '_' + str(test_percent))) == False

    def get_fitted_model(self, name, test_percent=25, need_fit=False):
        if self.need_fit_model(name, test_percent) or need_fit:
            self.xTrain, self.xTest, self.yTrain, self.yTest = self.get_train_test_data(test_percent / 100)
            self.methods[name] = self.methods[name].fit(self.xTrain, self.yTrain)
            with open(self.get_pickled_file_name(name + '_' + str(test_percent)), 'wb') as f:
                pickle.dump(self.methods[name], f)
        else:
            with open(self.get_pickled_file_name(name + '_' + str(test_percent)), 'rb') as f:
                self.methods[name] = pickle.load(f)

        return self.methods[name]

    def calculate_sensitivity(self, yPred):
        sick_test_cnt = len(self.yTest[self.yTest == 1])
        sick_pred_cnt = len(yPred[yPred == 1])
        return sick_pred_cnt / sick_test_cnt

    def calculate_specificity(self, yPred):
        healthy_test_cnt = len(self.yTest[self.yTest == 0])
        healthy_pred_cnt = len(yPred[yPred == 0])
        return healthy_pred_cnt / healthy_test_cnt
