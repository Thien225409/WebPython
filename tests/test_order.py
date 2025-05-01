import pytest
from types import SimpleNamespace

from models.cart import Cart
from models.order import Order
from models.product import Product
from controllers.order_controller import list as list_orders, checkout
from tests.conftest import fake_request

class DummyProduct:
    def __init__(self, product_id, price):
        self.product_id = product_id
        self.price = price


def test_checkout_creates_order_and_clears_cart(monkeypatch):
    user = SimpleNamespace(user_id=2)
    # Setup fake cart data
    cart_data = {2: {10: 3}}
    monkeypatch.setattr(Cart, 'get_items', lambda uid: cart_data.get(uid, {}))
    removed = []
    monkeypatch.setattr(Cart, 'remove_item', lambda uid, pid: removed.append(pid))

    # Stub Product and Order.create
    monkeypatch.setattr(Product, 'find_by_id', lambda pid: DummyProduct(pid, price=200))
    created = {}
    def fake_create(uid, items, total):
        created['uid'] = uid
        created['items'] = items
        created['total'] = total
        return 123
    monkeypatch.setattr(Order, 'create', fake_create)

    # Stub CSRF verification
    monkeypatch.setattr('controllers.order_controller.verify_csrf', lambda req: True)

    # Perform checkout
    req = fake_request(method='POST', path='/checkout', cookies={'csrf_token': 'tok'}, user=user)
    status, headers, _ = checkout(req)

    assert status.startswith('303')
    assert any(k == 'Location' and v == '/orders' for k, v in headers)
    # Verify Order.create called correctly
    assert created['uid'] == 2
    assert created['total'] == 200 * 3
    # Verify cart items cleared
    assert removed == [10]


def test_list_orders_renders_template(monkeypatch):
    user = SimpleNamespace(user_id=2)
    # Stub order list and template rendering
    fake_orders = [{'Id': 50, 'Total': 500, 'CreatedAt': '2025-05-02'}]
    monkeypatch.setattr(Order, 'list_by_user', lambda uid: fake_orders)
    monkeypatch.setattr('controllers.order_controller.gen_csrf_token', lambda: 'csrf')
    monkeypatch.setattr('controllers.order_controller.render_template', lambda tpl, ctx, request=None: tpl)

    req = fake_request(method='GET', path='/orders', user=user)
    status, headers, body = list_orders(req)

    assert status == '200 OK'
    assert body == 'orders.html'
