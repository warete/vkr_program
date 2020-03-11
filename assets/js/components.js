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
                    name: 'svm'
                },
                1: {
                    name: 'k-ближайших соседей'
                }
            },
            selectedMethod: 0,
            apiBase: 'http://localhost:5000',
            apiRoutes: {
                trainData: '/train/',
                predictData: '/predict/'
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
        doTrain: function () {
            console.log('training start...');
        },
        doPredict: function () {
            console.log('predicting start...');
        }
    }
});