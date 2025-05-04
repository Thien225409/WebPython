import os, sys
from types import SimpleNamespace
import pytest
from urllib.parse import urlencode

# Ensure project root in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import controllers.auth_controller as auth_ctrl
from controllers.auth_controller import register, login, logout, parse_cookies

class FakeRequest(SimpleNamespace):
    def __init__(self, method='GET', path='/', body=b'', headers=None, params=None, cookies=None):
        headers = headers or {}
        params = params or {}
        cookies = cookies or {}
        query = params
        super().__init__(method=method, path=path, headers=headers,
                         body=body, params=params, cookies=cookies, query=query)

@pytest.fixture(autouse=True)
def patch_csrf_and_render(monkeypatch):
    monkeypatch.setattr(auth_ctrl, 'gen_csrf_token', lambda: 'fixed-csrf')
    monkeypatch.setattr(auth_ctrl, 'verify_csrf', lambda req: True)
    monkeypatch.setattr(auth_ctrl, 'render_template',
                        lambda tpl, ctx, request=None: f"<html tpl={tpl} ctx={ctx}>")
    yield

# -- parse_cookies tests --
@pytest.mark.parametrize("header,expected", [
    ("k1=v1; k2=v2", {"k1":"v1","k2":"v2"}),
    ("novalue; x=y", {"x":"y"}),
    ("", {}),
])
def test_parse_cookies(header, expected):
    assert parse_cookies(header) == expected

# -- register tests --
def test_register_get_shows_form():
    req = FakeRequest(method='GET')
    status, headers, html = register(req)
    assert status == '200 OK'
    assert '<html tpl=register.html' in html

def test_register_post_csrf_fail(monkeypatch):
    monkeypatch.setattr(auth_ctrl, 'verify_csrf', lambda req: False)
    body = urlencode({
        'username': 'u',
        'password': 'passw',
        'confirm_password': 'passw',
        'email': 'a@b.c'
    }).encode()
    req = FakeRequest(method='POST', body=body, headers={'Cookie': ''})
    status, headers, resp = register(req)
    assert status == '403 Forbidden'
    assert 'CSRF token không hợp lệ' in resp

def test_register_post_password_too_short():
    # password dưới 5 ký tự
    body = urlencode({
        'username': 'newuser',
        'password': 'shor',  # 4 ký tự
        'confirm_password': 'shor',
        'email': 'u@example.com'
    }).encode()
    req = FakeRequest(method='POST', body=body, headers={'Cookie': 'csrf_token=fixed-csrf'})
    status, headers, html = register(req)
    assert status.startswith('400')
    assert 'Mật khẩu phải từ 5 ký tự trở lên.' in html

def test_register_post_password_mismatch():
    body = urlencode({
        'username': 'newuser',
        'password': 'password1',
        'confirm_password': 'password2',
        'email': 'u@example.com'
    }).encode()
    req = FakeRequest(method='POST', body=body, headers={'Cookie': 'csrf_token=fixed-csrf'})
    status, headers, html = register(req)
    assert status.startswith('400')
    assert 'Mật khẩu nhập lại không khớp' in html

def test_register_post_duplicate_username(monkeypatch):
    class DummyUser:
        @staticmethod
        def register(u, p, e):
            raise ValueError("Tên đăng nhập đã tồn tại.")
    monkeypatch.setattr(auth_ctrl, 'User', DummyUser)
    body = urlencode({
        'username': 'taken',
        'password': 'longpwd123',
        'confirm_password': 'longpwd123',
        'email': 't@t.t'
    }).encode()
    req = FakeRequest(method='POST', body=body, headers={'Cookie': 'csrf_token=fixed-csrf'})
    status, headers, html = register(req)
    assert status == '400 Bad Request'
    assert 'Tên đăng nhập đã tồn tại' in html

def test_register_post_success(monkeypatch):
    created = {}
    class DummyUser:
        @staticmethod
        def register(u, p, e):
            created.update({'u': u, 'p': p, 'e': e})
    monkeypatch.setattr(auth_ctrl, 'User', DummyUser)
    body = urlencode({
        'username': 'okuser',
        'password': 'longpwd123',
        'confirm_password': 'longpwd123',
        'email': 'ok@e.com'
    }).encode()
    req = FakeRequest(method='POST', body=body, headers={'Cookie': 'csrf_token=fixed-csrf'})
    status, headers, _ = register(req)
    assert status == '303 See Other'
    assert ('Location', '/login') in headers
    assert created == {'u': 'okuser', 'p': 'longpwd123', 'e': 'ok@e.com'}

# -- login tests --
def test_login_get_shows_form():
    req = FakeRequest(method='GET', params={'next': ['/home']})
    status, headers, html = login(req)
    assert status == '200 OK'
    assert '<html tpl=login.html' in html
    assert any(h[0] == 'Set-Cookie' and 'csrf_token=fixed-csrf' in h[1] for h in headers)

# -- logout tests --
def test_logout_clears_all_cookies(monkeypatch):
    cleans = []
    monkeypatch.setattr(auth_ctrl, 'delete_session', lambda sid: cleans.append(sid))
    req = FakeRequest(method='GET', headers={'Cookie': 'session_id=abc; csrf_token=tok'})
    status, headers, _ = logout(req)
    assert status == '303 See Other'
    sc = [v for k, v in headers if k == 'Set-Cookie']
    assert any('session_id=; Path=/; Max-Age=0' in c for c in sc)
    assert any('csrf_token=; Path=/; Max-Age=0' in c for c in sc)
    assert cleans == ['abc']
    assert ('Location','/login') in headers

