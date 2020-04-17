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
    props: ['methods', 'patientResult'],
    data: function () {
        return {
            importFilePath: '',
            testPercent: 25,
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

Vue.component('recipient-form', {
    props: ['patientResult'],
    data: function () {
        return {
            rt: [],
            ik: []
        }
    },
    computed: {
        patientResultFull: function() {
            return this.patientResult.class ? this.patientResult.class : '';
        }
    },
    watch: {
        rt: function (newVal) {
            this.$root.$emit('rt_changed', newVal);
        },
        ik: function (newVal) {
            this.$root.$emit('ik_changed', newVal);
        },
    },
    template: '#template-recipient-form',
    created: function() {
        for (let i = 0; i < 9; i++) {
            this.rt.push('');
            this.ik.push('');
        }
    },
    methods: {
        onDiagnoseHandler: function() {
            const empty_rt = this.rt.filter(item => item.length == 0);
            const empty_ik = this.ik.filter(item => item.length == 0);
            if (empty_ik.length || empty_rt.length) {
                this.$root.$emit('show_toast', 'Не все данные пациента заполнены', 'error');
            } else {
                this.$root.$emit('do_diagnose', {
                    rt: this.rt,
                    ik: this.ik
                });
            }
        }
    }
});

var app = new Vue({
    el: '#app',
    data: function() {
        return {
            importFilePath: '',
            testPercent: 25,
            methods: {
                0: {
                    name: 'svm',
                    code: 'svm',
                    canPredict: true,
                    metrics: {
                        sensitivity: 0,
                        specificity: 0,
                        accuracy: []
                    }
                },
                1: {
                    name: 'k-ближайших соседей',
                    code: 'knn',
                    canPredict: true,
                    metrics: {
                        sensitivity: 0,
                        specificity: 0,
                        accuracy: []
                    }
                },
                2: {
                    name: 'Bagging meta-estimator + SVM',
                    code: 'bagging',
                    canPredict: true,
                    metrics: {
                        sensitivity: 0,
                        specificity: 0,
                        accuracy: []
                    }
                },
                3: {
                    name: 'Stochastic Gradient Descent',
                    code: 'sgd',
                    canPredict: true,
                    metrics: {
                        sensitivity: 0,
                        specificity: 0,
                        accuracy: []
                    }
                }
            },
            selectedMethod: 0,
            apiBase: window.appHost ? window.appHost : 'http://127.0.0.1:5000/',
            apiRoutes: {
                trainData: 'train/',
                predictData: 'predict/',
                staticMetrics: 'static_metrics/',
                diagnose: 'diagnose/',
            },
            frequencyTemperature: {
                data: [],
                layout: {
                    title: 'Распределение температуры по точкам',
                    plot_bgcolor: '#F4F4F4',
                    paper_bgcolor: '#F4F4F4'
                }
            },
            frequencyTumor: {
                data: [],
                layout: {
                    title: 'Частотное распределение опухолей по точкам',
                    plot_bgcolor: '#F4F4F4',
                    paper_bgcolor: '#F4F4F4'
                }
            },
            mainAccuracy: {
                data: [
                    {
                        values: [],
                        type: 'pie',
                        labels: ['Верно', 'Неверно'],
                        showlegend: false,
                        automargin: true
                    }
                ],
                layout: {
                    title: 'Точность "здоров/болен"',
                    plot_bgcolor: '#F4F4F4',
                    paper_bgcolor: '#F4F4F4'
                }
            },
            patientResult: {
                class: null,
                point: null
            }
        }
    },
    computed: {
        sensitivity: function () {
            return typeof this.methods[this.selectedMethod].metrics.sensitivity != 'undefined' ? this.methods[this.selectedMethod].metrics.sensitivity : 0;
        },
        specificity: function () {
            return typeof this.methods[this.selectedMethod].metrics.specificity != 'undefined' ? this.methods[this.selectedMethod].metrics.specificity : 0;
        },
        mainAccuracyData: function () {
            const values = this.methods[this.selectedMethod].metrics.accuracy.length ? this.methods[this.selectedMethod].metrics.accuracy : [1, 0];
            const data = [...this.mainAccuracy.data];
            data[0].values = values;
            return data;
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
        this.$on('do_diagnose', function (data) {
            this.doDiagnose(data);
        });
        this.$on('show_toast', function (message, type) {
            this.showToast(message, type);
        });
    },
    mounted: function () {
        this.sendRequest(
            this.apiRoutes.staticMetrics,
            null,
            (res) => {
                if (res.data.status == 'success') {
                    if (typeof res.data.metrics.frequencyTemperature != undefined) {
                        const freqData = [];
                        for (let i in res.data.metrics.frequencyTemperature) {
                            freqData.push({
                                y: Object.values(res.data.metrics.frequencyTemperature[i]), 
                                type: 'box',
                                name: i,
                                automargin: true
                            });
                        }
                        this.frequencyTemperature.data = freqData;
                    }
                    if (typeof res.data.metrics.frequencyTumor != undefined) {                        
                        this.frequencyTumor.data = [{
                            x: Object.values(res.data.metrics.frequencyTumor.x), 
                            y: Object.values(res.data.metrics.frequencyTumor.y),
                            type: 'bar',
                            automargin: true
                        }];
                    }
                } else {
                    this.showToast('Произошла ошибка во время получения статистических данных', 'error');
                }
            }
        );
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
            this.sendRequest(
                this.apiRoutes.trainData,
                {
                    method: this.methods[this.selectedMethod].code,
                    methodId: this.selectedMethod,
                    testPercent: this.testPercent
                },
                (res) => {
                    if (res.data.status == 'success') {
                        this.methods[res.data.method.id].canPredict = true;
                        this.showToast('Обучение прошло успешно. Теперь можно запустить', 'success');
                    } else {
                        this.showToast('Попробуйте позже', 'error');
                    }
                }
            );
        },
        doPredict: function () {
            if (this.methods[this.selectedMethod].canPredict) {
                this.sendRequest(
                    this.apiRoutes.predictData,
                    {
                        method: this.methods[this.selectedMethod].code,
                        testPercent: this.testPercent
                    },
                    (res) => {
                        if (res.data.status == 'success') {
                            this.methods[this.selectedMethod].metrics['accuracy'] = [res.data.metrics.accuracy, 1 - res.data.metrics.accuracy];
                            if (typeof res.data.metrics.sensitivity != undefined) {
                                this.methods[this.selectedMethod].metrics['sensitivity'] = res.data.metrics.sensitivity;
                            }
                            if (typeof res.data.metrics.specificity != undefined) {
                                this.methods[this.selectedMethod].metrics['specificity'] = res.data.metrics.specificity;
                            }                            
                            this.showToast('Данные успешно получены', 'success');
                        } else if (res.data.status == 'warning') {
                            this.showToast(res.data.message, 'warning');
                        } else {
                            this.showToast('Попробуйте позже', 'error');
                        }
                    }
                );
            } else {
                this.showToast('Нужно сначала обучить', 'warning');
            }
        },
        doDiagnose: function (data) {
            this.sendRequest(
                this.apiRoutes.diagnose,
                {
                    method: this.methods[this.selectedMethod].code,
                    patientData: data,
                    testPercent: this.testPercent
                },
                (res) => {
                    if (res.data.status == 'success') {
                        this.patientResult.class = res.data.result.class;                     
                        this.showToast((this.patientResult.class == 1 ? 'Болен' : 'Здоров'), 'success');
                    } else if (res.data.status == 'warning') {
                        this.showToast(res.data.message, 'warning');
                    } else {
                        this.showToast('Попробуйте позже', 'error');
                    }
                }
            );
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
            };
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