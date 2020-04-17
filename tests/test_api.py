from app import app
import json


class TestApi:
    def setup_class(self):
        self.client = app.test_client()

    def test_index_route_status_200(self):
        result = self.client.get('/')
        assert result.status_code == 200

    def test_static_metrics_route_status_200(self):
        result = self.client.post('/static_metrics/', data={})
        assert result.status_code == 200
        result = self.client.get('/static_metrics/', data={})
        assert result.status_code != 200

    def test_train_route_send_not_supported_request_type(self):
        result = self.client.get('/train/', data=json.dumps({}))
        assert result.status_code != 200

    def test_predict_route_send_not_supported_request_type(self):
        result = self.client.get('/predict/', data=json.dumps({}))
        assert result.status_code != 200

    def test_static_metrics_route_body_status_is_success(self):
        result = self.client.post('/static_metrics/', data=json.dumps({}))
        assert result.status_code == 200
        assert json.loads(result.data)['status'] == 'success'

    def test_static_metrics_route_has_metrics_in_body(self):
        result = self.client.post('/static_metrics/', data=json.dumps({}))
        decoded_data = json.loads(result.data)
        assert result.status_code == 200
        assert 'metrics' in decoded_data
        assert 'frequencyTemperature' in decoded_data['metrics']
        assert 'frequencyTumor' in decoded_data['metrics']

    def test_train_route_not_supported_method(self):
        result = self.client.post('/train/', data=json.dumps({'method': ''}))
        decoded_data = json.loads(result.data)
        assert result.status_code == 200
        assert decoded_data['status'] == 'error'

    def test_predict_route_not_supported_method(self):
        result = self.client.post('/predict/', data=json.dumps({'method': ''}))
        decoded_data = json.loads(result.data)
        assert result.status_code == 200
        assert decoded_data['status'] == 'error'
