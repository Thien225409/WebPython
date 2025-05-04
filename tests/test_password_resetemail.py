import os, sys
from datetime import datetime
from urllib.parse import urlencode
import pytest

# Ensure project root in sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import controllers.auth_controller as auth_ctrl
from controllers.auth_controller import forgot_password
from config import APP_HOST

class FakeRequest:
    def __init__(self, method='POST', body=b'', headers=None):
        self.method = method
        self.body = body
        self.headers = headers or {}

@pytest.fixture(autouse=True)
def patch_csrf_and_render(monkeypatch):
    # Always verify CSRF and no-op template rendering
    monkeypatch.setattr(auth_ctrl, 'verify_csrf', lambda req: True)
    monkeypatch.setattr(auth_ctrl, 'render_template', lambda tpl, ctx, request=None: '<html>')
    yield

def test_forgot_password_sends_email(monkeypatch):
    # Stub user lookup
    class DummyUser:
        user_id = 100
        username = 'testuser'
        email = 'test@example.com'
    monkeypatch.setattr(auth_ctrl.User, 'find_by_username', lambda u: DummyUser)

    # Capture token persistence
    created = {}
    class StubPRT:
        @staticmethod
        def create(token, uid, expires):
            created.update({'token': token, 'uid': uid, 'expires': expires})
    monkeypatch.setattr(auth_ctrl, 'PasswordResetToken', StubPRT)

    # Stub SMTP to capture email
    sent = {}
    class StubSMTP:
        def __init__(*args, **kwargs): pass
        def starttls(self): pass
        def login(self, u, p): pass
        def send_message(self, msg):
            sent['to'] = msg['To']
            sent['subject'] = msg['Subject']
            sent['body'] = msg.get_content()
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): pass
    monkeypatch.setattr(auth_ctrl.smtplib, 'SMTP', lambda *a, **k: StubSMTP())

    # Execute endpoint
    body = urlencode({'username':'testuser','email':'test@example.com'}).encode()
    req = FakeRequest(body=body, headers={'Cookie':'csrf_token=tok'})
    status, headers, html = forgot_password(req)

    assert status == '200 OK'
    # Token saved correctly
    assert created['uid'] == 100
    assert isinstance(created['expires'], datetime)
    # Email sent to correct address
    assert sent['to'] == 'test@example.com'
    assert 'Đặt lại mật khẩu' in sent['subject']
    # Link contains APP_HOST and token
    assert f"{APP_HOST}/reset-password?token={created['token']}" in sent['body']

def test_forgot_password_no_email_on_invalid_user(monkeypatch):
    # No user found
    monkeypatch.setattr(auth_ctrl.User, 'find_by_username', lambda u: None)
    # Track SMTP calls
    called = {'sent': False}
    class StubSMTP:
        def __init__(*args, **kwargs): pass
        def starttls(self): pass
        def login(self, u, p): pass
        def send_message(self, msg):
            called['sent'] = True
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): pass
    monkeypatch.setattr(auth_ctrl.smtplib, 'SMTP', lambda *a, **k: StubSMTP())

    body = urlencode({'username':'nouser','email':'no@example.com'}).encode()
    req = FakeRequest(body=body, headers={'Cookie':'csrf_token=tok'})
    status, headers, html = forgot_password(req)

    assert status == '200 OK'
    assert not called['sent']