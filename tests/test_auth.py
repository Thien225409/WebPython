import pytest
from urllib.parse import urlencode
from controllers import auth_controller as auth
from models.users import User
from utils.security import verify_password
from utils.conftest import fake_request

def test_register_success():
    body = urlencode({
        'username': 'pytest_user',
        'password': 'abc123',
        'csrf_token': 'xyz123'
    })
    cookies = {'csrf_token': 'xyz123'}
    req = fake_request(method='POST', path='/register', body=body, cookies=cookies)

    status, headers, _ = auth.register(req)

    assert status.startswith('303')
    assert any(h[0] == 'Location' and h[1] == '/login' for h in headers)

    u = User.find_by_username('pytest_user')
    assert u is not None
    assert u.check_password('abc123')

def test_register_csrf_fail():
    body = urlencode({'username': 'csrf_fail', 'password': 'abc'})
    req = fake_request(method='POST', path='/register', body=body)

    status, _, body = auth.register(req)
    assert status == '403 Forbidden'
    assert 'CSRF' in body
