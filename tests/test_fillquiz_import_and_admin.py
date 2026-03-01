import json
from app import create_app


def test_import_and_admin_routes(tmp_path):
    app = create_app({'TESTING': True, 'WTF_CSRF_ENABLED': False})
    app.debug = True
    with app.app_context():
        client = app.test_client()
        # call import endpoint
        r = client.post('/admin/import-fill-questions')
        assert r.status_code == 200
        data = r.get_json()
        assert 'imported' in data

        # start a quiz
        r2 = client.get('/fillquiz/start?size=10')
        assert r2.status_code == 200
        start = r2.get_json()
        assert 'attempt_id' in start

        # access admin list page
        r3 = client.get('/admin/fillquestions')
        assert r3.status_code == 200
        html = r3.get_data(as_text=True)
        assert 'Fill Questions' in html