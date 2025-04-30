# tests/test_auth.py
import os, sys
# Đưa project root vào sys.path để tìm package controllers
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from types import SimpleNamespace
from urllib.parse import urlencode
from controllers.auth_controller import render_form, register, login, parse_cookies, logout

# Dummy User model để avoid side-effects
class DummyUser:
    def __init__(self, user_id, username, password_ok=True):
        self.user_id = user_id
        self._password_ok = password_ok

    @staticmethod
    def register(username, password):
        if username == 'taken':
            raise ValueError("Duplicate username")

    @staticmethod
    def find_by_username(username):
        if username == 'valid':
            return DummyUser(user_id=1, username='valid')
        return None

    def check_password(self, password):
        return self._password_ok

# Fake Request object
class FakeRequest(SimpleNamespace):
    def __init__(self, method='GET', path='/', body=b'', headers=None, params=None):
        headers = headers or {}
        super().__init__(method=method, path=path, headers=headers, body=body, params=params or {})

@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Patch CSRF token funcs
    monkeypatch.setattr('controllers.auth_controller.gen_csrf_token', lambda: 'fixed-token')
    monkeypatch.setattr('controllers.auth_controller.verify_csrf', lambda req: True)
    # Patch template engine
    monkeypatch.setattr('controllers.auth_controller.render_template',
                        lambda tpl, ctx, request=None: f"<html tpl={tpl} ctx={ctx}>")
    # Patch User and session funcs
    monkeypatch.setattr('controllers.auth_controller.User', DummyUser)
    monkeypatch.setattr('controllers.auth_controller.create_session', lambda uid: 'session123')
    monkeypatch.setattr('controllers.auth_controller.delete_session', lambda sid: None)
    yield

@pytest.mark.parametrize("header,expected", [
    ("k1=v1; k2=v2", {"k1":"v1","k2":"v2"}),
    ("k1=v1;k2=v2", {"k1":"v1","k2":"v2"}),
    (" a = b ;c=d; e = f ", {"a":"b","c":"d","e":"f"}),
    ("", {}),
    ("novalue; x=y", {"x":"y"}),
])
def test_parse_cookies(header, expected):
    assert parse_cookies(header) == expected


def test_render_form_sets_csrf_cookie_and_renders():
    req = FakeRequest(method='GET')
    status, headers, html = render_form('login.html', req)
    assert status == '200 OK'
    cookie_header = dict(headers)['Set-Cookie']
    assert 'csrf_token=fixed-token' in cookie_header
    assert '<html tpl=login.html' in html


def test_register_get():
    req = FakeRequest(method='GET')
    status, headers, html = register(req)
    assert status == '200 OK'
    assert 'register.html' in html


def test_register_post_csrf_fail(monkeypatch):
    monkeypatch.setattr('controllers.auth_controller.verify_csrf', lambda req: False)
    body = urlencode({'username':'u','password':'p'}).encode()
    req = FakeRequest(method='POST', body=body)
    status, headers, html = register(req)
    assert status == '403 Forbidden'
    assert 'CSRF token không hợp lệ' in html


def test_register_post_success():
    body = urlencode({'username':'new','password':'p'}).encode()
    req = FakeRequest(method='POST', body=body, headers={'Cookie':'csrf_token=fixed-token'})
    status, headers, html = register(req)
    assert status.startswith('303')
    assert ('Location','/login') in headers


def test_register_post_duplicate():
    body = urlencode({'username':'taken','password':'p'}).encode()
    req = FakeRequest(method='POST', body=body, headers={'Cookie':'csrf_token=fixed-token'})
    status, headers, html = register(req)
    assert status == '400 Bad Request'
    assert 'Tên đăng nhập đã tồn tại.' in html


def test_login_get():
    req = FakeRequest(method='GET')
    status, headers, html = login(req)
    assert status == '200 OK'
    assert 'login.html' in html


def test_login_post_csrf_fail(monkeypatch):
    monkeypatch.setattr('controllers.auth_controller.verify_csrf', lambda req: False)
    body = urlencode({'username':'u','password':'p'}).encode()
    req = FakeRequest(method='POST', body=body)
    status, headers, html = login(req)
    assert status == '403 Forbidden'


def test_login_post_success():
    body = urlencode({'username':'valid','password':''}).encode()
    req = FakeRequest(method='POST', body=body, headers={'Cookie':'csrf_token=fixed-token'})
    status, headers, html = login(req)
    assert status.startswith('303')
    cookies = [v for k,v in headers if k=='Set-Cookie']
    assert any('session_id=session123' in c for c in cookies)
    assert any('csrf_token=fixed-token' in c for c in cookies)


def test_login_post_wrong_credentials():
    body = urlencode({'username':'wrong','password':'p'}).encode()
    req = FakeRequest(method='POST', body=body, headers={'Cookie':'csrf_token=fixed-token'})
    status, headers, html = login(req)
    assert status == '400 Bad Request'
    assert 'Tên đăng nhập hoặc mật khẩu không đúng.' in html


def test_logout():
    req = FakeRequest(method='GET', headers={'Cookie':'session_id=sid; csrf_token=tok'})
    status, headers, html = logout(req)
    assert status.startswith('303')
    set_cookies = [v for k,v in headers if k=='Set-Cookie']
    assert any('session_id=' in c and 'Max-Age=0' in c for c in set_cookies)
    assert any('csrf_token=' in c and 'Max-Age=0' in c for c in set_cookies)
    assert ('Location','/login') in headers
