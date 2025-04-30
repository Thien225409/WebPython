import pytest
from controllers.product_controller import form as product_form
from controllers.auth_controller import login as auth_login, logout as auth_logout
from models import Product
from models.users import User
from config import ADMIN_PASSWORD
from urllib.parse import urlencode
from tests.conftest import fake_request
from sessions.session_manager import create_session, get_session
# import sessions.session_manager as sm  # Không còn dùng file-based sessions
from routes.auth_middleware import require_auth
from datetime import datetime, timedelta, timezone

@pytest.fixture
def admin_user():
    user = User.find_by_username('admin')
    user.is_admin = True
    return user

# -- Test form GET sản phẩm --
def test_get_new_product_form(admin_user):
    req = fake_request(method='GET', path='/product/new', cookies={}, user=admin_user)
    status, headers, html = product_form(req)
    assert status == '200 OK'
    raw = [v for k, v in headers if k == 'Set-Cookie' and 'csrf_token=' in v][0]
    token = raw.split('=')[1].split(';')[0]
    assert any(k=='Set-Cookie' and 'csrf_token=' in v for k,v in headers)
    assert f'name="csrf_token" value="{token}"' in html


def test_get_edit_product_form(admin_user):
    p = Product.create('Sản phẩm edit', 10000, 1, 'Mô tả', '/img.png')
    req = fake_request(
        method='GET',
        path=f'/product/{p.product_id}/edit',
        cookies={},
        user=admin_user,
        params={'product_id': str(p.product_id)}
    )
    status, headers, html = product_form(req)
    assert status == '200 OK'
    assert f'value="{p.name}"' in html
    assert str(p.price) in html
    raw = [v for k, v in headers if k == 'Set-Cookie' and 'csrf_token=' in v][0]
    token = raw.split('=')[1].split(';')[0]
    assert f'name="csrf_token" value="{token}"' in html

# -- Test đăng nhập/đăng xuất và session --
def test_get_login_form():
    req = fake_request(method='GET', path='/login')
    status, headers, html = auth_login(req)
    assert status == '200 OK'
    assert 'name="csrf_token"' in html
    assert any(k=='Set-Cookie' and 'csrf_token=' in v for k,v in headers)


def test_login_success():
    _, headers, _ = auth_login(fake_request(method='GET', path='/login'))
    token = [v for k,v in headers if k=='Set-Cookie' and 'csrf_token=' in v][0].split('=')[1].split(';')[0]
    body = urlencode({'username': 'admin', 'password': ADMIN_PASSWORD, 'csrf_token': token})
    req = fake_request(method='POST', path='/login', body=body, cookies={'csrf_token': token})
    status, headers, _ = auth_login(req)
    assert status.startswith('303')
    assert any(k=='Set-Cookie' and 'session_id=' in v for k,v in headers)
    assert any(k=='Location' and v=='/product' for k,v in headers)


def test_login_wrong_credentials():
    _, headers, _ = auth_login(fake_request(method='GET', path='/login'))
    token = [v for k,v in headers if k=='Set-Cookie' and 'csrf_token=' in v][0].split('=')[1].split(';')[0]
    body = urlencode({'username': 'admin', 'password': 'wrong', 'csrf_token': token})
    req = fake_request(method='POST', path='/login', body=body, cookies={'csrf_token': token})
    status, headers, html = auth_login(req)
    assert status == '400 Bad Request'
    assert 'Tên đăng nhập hoặc mật khẩu không đúng' in html


def test_logout_clears_cookies():
    sid = create_session(1)
    req = fake_request(method='GET', path='/logout', cookies={'session_id': sid, 'csrf_token': 'x'})
    status, headers, _ = auth_logout(req)
    assert status.startswith('303')
    assert any(k=='Location' and v=='/login' for k,v in headers)
    sc = [v for k,v in headers if k=='Set-Cookie']
    assert any('session_id=' in c and 'Max-Age=0' in c for c in sc)

# -- Middleware require_auth tests --
def dummy_handler(req):
    return ('200 OK', [], 'OK')
protected = require_auth(dummy_handler)

def test_require_auth_redirects_anonymous():
    req = fake_request(user=None)
    status, headers, _ = protected(req)
    assert status.startswith('303')
    assert any(v=='/login' for _,v in headers)


def test_require_auth_allows_logged_in():
    user = User.find_by_username('admin')
    user.is_admin = True
    req = fake_request(user=user)
    status, headers, body = protected(req)
    assert status == '200 OK'
    assert body == 'OK'

# -- Session expire test --
from database import get_conn

def test_session_expire():
    # Tạo session mới (DB-backed)
    sid = create_session(1)
    # Giả lập session đã hết hạn trong DB
    past = datetime.now(timezone.utc) - timedelta(hours=2)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE dbo.Sessions SET ExpiresAt = ? WHERE SessionId = ?", 
        past.isoformat(), sid
    )
    try:
        conn.commit()
    except Exception:
        pass
    # Khi gọi get_session, session phải bị coi là hết hạn
    assert get_session(sid) is None
