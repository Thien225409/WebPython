import pytest
from types import SimpleNamespace
from urllib.parse import urlencode

from models.cart import Cart
from models.order import Order
from controllers.cart_controller import view, add, remove
from controllers.order_controller import list as list_orders, checkout
from tests.conftest import fake_request

# -- Tests for Cart CSRF & Session --

def test_view_sets_csrf_cookie(monkeypatch):
    user = SimpleNamespace(user_id=1)
    # stub Cart.get_items and template/CSRF
    monkeypatch.setattr(Cart, 'get_items', lambda uid: {})
    monkeypatch.setattr('controllers.cart_controller.gen_csrf_token', lambda: 'csrf-123')
    monkeypatch.setattr('controllers.cart_controller.render_template', lambda tpl, ctx, request=None: tpl)

    req = fake_request(method='GET', path='/cart', user=user)
    status, headers, body = view(req)

    assert status == '200 OK'
    assert any(k == 'Set-Cookie' and 'csrf_token=csrf-123' in v for k, v in headers)
    assert body == 'cart.html'


def test_add_without_csrf_fails(monkeypatch):
    user = SimpleNamespace(user_id=1)
    storage = {}
    # stub add_item but CSRF fails
    monkeypatch.setattr(Cart, 'add_item', lambda uid, pid: storage.setdefault(uid, {}).__setitem__(pid, 1))
    monkeypatch.setattr('controllers.cart_controller.verify_csrf', lambda req: False)

    body_data = urlencode({'product_id': '5'}).encode()
    req = fake_request(method='POST', path='/cart/add', body=body_data, cookies={}, user=user)
    status, headers, body_resp = add(req)

    assert status == '403 Forbidden'
    assert 'CSRF token không hợp lệ.' in body_resp
    assert storage == {}


def test_remove_without_csrf_fails(monkeypatch):
    user = SimpleNamespace(user_id=1)
    storage = {1: {5: 2}}
    monkeypatch.setattr(Cart, 'remove_item', lambda uid, pid: storage[uid].pop(pid, None))
    monkeypatch.setattr('controllers.cart_controller.verify_csrf', lambda req: False)

    body_data = urlencode({'product_id': '5'}).encode()
    req = fake_request(method='POST', path='/cart/remove', body=body_data, cookies={}, user=user)
    status, headers, body_resp = remove(req)

    assert status == '403 Forbidden'
    assert 'CSRF token không hợp lệ.' in body_resp
    assert storage[1][5] == 2  # not removed

# -- Tests for Order CSRF & Session --

def test_list_orders_sets_csrf_cookie(monkeypatch):
    user = SimpleNamespace(user_id=2)
    monkeypatch.setattr(Order, 'list_by_user', lambda uid: [])
    monkeypatch.setattr('controllers.order_controller.gen_csrf_token', lambda: 'csrf-xyz')
    monkeypatch.setattr('controllers.order_controller.render_template', lambda tpl, ctx, request=None: tpl)

    req = fake_request(method='GET', path='/orders', user=user)
    status, headers, body = list_orders(req)

    assert status == '200 OK'
    assert any(k == 'Set-Cookie' and 'csrf_token=csrf-xyz' in v for k, v in headers)
    assert body == 'orders.html'


def test_list_orders_requires_login():
    req = fake_request(method='GET', path='/orders', user=None)
    status, headers, body = list_orders(req)

    assert status.startswith('303')
    assert any(k == 'Location' and v == '/login' for k, v in headers)


def test_checkout_get_redirect():
    user = SimpleNamespace(user_id=3)
    req = fake_request(method='GET', path='/checkout', user=user)
    status, headers, body = checkout(req)

    assert status.startswith('303')
    assert any(k == 'Location' and v == '/orders' for k, v in headers)


def test_checkout_without_csrf_fails(monkeypatch):
    user = SimpleNamespace(user_id=3)
    monkeypatch.setattr('controllers.order_controller.verify_csrf', lambda req: False)

    req = fake_request(method='POST', path='/checkout', cookies={}, user=user)
    status, headers, body = checkout(req)

    assert status == '403 Forbidden'
    assert 'CSRF token không hợp lệ.' in body
