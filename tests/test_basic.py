def test_index_shows_home(client):
    res = client.get('/')
    assert res.status_code in (200, 302)


def test_admin_create_list(client):
    res = client.post('/admin/list/new', data={'name': 'Test List', 'description': 'desc'}, follow_redirects=True)
    assert res.status_code == 200
    assert b'Test List' in res.data
