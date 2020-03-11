Vue.component("vue-plotly", {
    props: ["data", "layout", "uid"],
    template: '<div :ref="uid"></div>',
    mounted() {
        Plotly.plot(this.$refs[this.uid], this.data, this.layout, {displaylogo: false, responsive: true});
    },
    watch: {
        data: {
            handler: function () {
                Plotly.react(
                    this.$refs[this.uid],
                    this.data,
                    this.layout,
                    {displaylogo: false}
                );
            },
            deep: true
        }
    }
});

Vue.component('left-form', {
    props: ['methods'],
    data: function () {
        return {
            importFilePath: '',
            testPercent: 75,
            selectedMethod: 0
        }
    },
    computed: {
        methodsForSelect: function () {
            const methods = this.methods;
            return Object.keys(this.methods).map(key => ({value: key, text: methods[key].name}));
        }
    },
    watch: {
        importFilePath: function (newVal) {
            this.$root.$emit('import_file_path_changed', newVal);
        },
        testPercent: function (newVal) {
            this.$root.$emit('test_percent_changed', newVal);
        },
        selectedMethod: function (newVal) {
            this.$root.$emit('selected_method_changed', newVal);
        }
    },
    template: '#template-left-form',
    methods: {
        onTrainHandler: function() {
            this.$root.$emit('do_train');
        },
        onPredictHandler: function() {
            this.$root.$emit('do_predict');
        }
    }
});

var app = new Vue({
    el: '#app',
    data: function() {
        return {
            importFilePath: '',
            testPercent: 75,
            methods: {
                0: {
                    name: 'svm',
                    code: 'svm',
                    canPredict: false
                },
                1: {
                    name: 'k-ближайших соседей',
                    code: 'knn',
                    canPredict: false
                },
                2: {
                    name: 'Bagging meta-estimator + SVM',
                    code: 'bagging',
                    canPredict: false
                },
                3: {
                    name: 'Stochastic Gradient Descent',
                    code: 'sgd',
                    canPredict: false
                }
            },
            selectedMethod: 0,
            apiBase: 'http://127.0.0.1:5000',
            apiRoutes: {
                trainData: '/train/',
                predictData: '/predict/'
            },
            mainAccuracyData: {
                data: [
                    {
                        values: [1, 0],
                        type: 'pie',
                        labels: ['Верно', 'Неверно'],
                        showlegend: false,
                        automargin: true
                    }
                ],
                layout: {
                    title: 'Точность "здоров/болен"'
                }
            }
        }
    },
    created: function () {
        this.$on('import_file_path_changed', function (data) {
            this.importFilePath = data;
        });
        this.$on('test_percent_changed', function (data) {
            this.testPercent = parseInt(data);
        });
        this.$on('selected_method_changed', function (data) {
            this.selectedMethod = parseInt(data);
        });
        this.$on('do_train', function () {
            this.doTrain();
        });
        this.$on('do_predict', function () {
            this.doPredict();
        });
    },
    methods: {
        sendRequest: function(endPoint, payload, callback) {
            axios.post(this.apiBase + endPoint, payload)
                .then(callback)
                .catch((error) => {
                    this.showToast(error, 'error');
                });
        },
        doTrain: function () {
            this.sendRequest(this.apiRoutes.trainData, {method: this.methods[this.selectedMethod].code, methodId: this.selectedMethod}, (res) => {
                if (res.data.status == 'success') {
                    this.methods[res.data.method.id].canPredict = true;
                    this.showToast('Обучение прошло успешно. Теперь можно запустить', 'success');
                } else {
                    this.showToast('Попробуйте позже', 'error');
                }
            });
        },
        doPredict: function () {
            if (this.methods[this.selectedMethod].canPredict) {
                this.sendRequest(this.apiRoutes.predictData, {method: this.methods[this.selectedMethod].code}, (res) => {
                    if (res.data.status == 'success') {
                        this.mainAccuracyData.data[0].values = [res.data.metrics.accuracy, 1 - res.data.metrics.accuracy];
                        this.showToast('Данные успешно получены', 'success');
                    } else {
                        this.showToast('Попробуйте позже', 'error');
                    }
                });
            } else {
                this.showToast('Нужно сначала обучить', 'warning');
            }
        },
        showToast: function (message, type) {
            const types = {
                error: {
                    title: 'Ошибка',
                    variant: 'danger'
                },
                warning: {
                    title: 'Предупреждение',
                    variant: 'warning'
                },
                success: {
                    title: 'Успешно',
                    variant: 'success'
                }
            }
            if (typeof types[type] != 'undefined') {
                this.$bvToast.toast(message, {
                    title: types[type].title,
                    autoHideDelay: 5000,
                    variant: types[type].variant
                });
            }
        }
    }
});