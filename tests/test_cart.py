import pytest
from urllib.parse import urlencode
from types import SimpleNamespace

from models.cart import Cart
from models.product import Product
from controllers.cart_controller import view, add, remove
from tests.conftest import fake_request  # fixture fake_request từ conftest.py :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}

class DummyProduct:
    def __init__(self, product_id, price, name='Test'):
        self.product_id = product_id
        self.price = price
        self.name = name

def test_add_view_remove_cart(monkeypatch):
    # chuẩn bị fake user và storage
    user = SimpleNamespace(user_id=1)
    storage = {}

    # stub Cart
    monkeypatch.setattr(Cart, 'get_items', lambda uid: storage.setdefault(uid, {}))
    monkeypatch.setattr(Cart, 'add_item', lambda uid, pid: storage.setdefault(uid, {}).__setitem__(pid, storage[uid].get(pid, 0) + 1))
    monkeypatch.setattr(Cart, 'remove_item', lambda uid, pid: storage.setdefault(uid, {}).pop(pid, None))

    # stub Product.find_by_id luôn trả DummyProduct
    monkeypatch.setattr(Product, 'find_by_id', lambda pid: DummyProduct(pid, price=150))

    # stub CSRF và template
    monkeypatch.setattr('controllers.cart_controller.verify_csrf', lambda req: True)
    monkeypatch.setattr('controllers.cart_controller.gen_csrf_token', lambda: 'fixed-token')
    monkeypatch.setattr('controllers.cart_controller.render_template', lambda tpl, ctx, request=None: tpl)

    # 1) Thêm sản phẩm vào giỏ
    body = urlencode({'product_id': '5'}).encode()
    req_add = fake_request(method='POST', path='/cart/add', body=body, cookies={'csrf_token': 'fixed-token'}, user=user)
    status_add, headers_add, _ = add(req_add)
    assert status_add.startswith('303')             # redirect sau khi add
    assert storage[1][5] == 1                       # storage đã cập nhật đúng

    # 2) Xem giỏ hàng
    req_view = fake_request(method='GET', path='/cart', user=user)
    status_view, headers_view, html_view = view(req_view)
    assert status_view == '200 OK'
    assert html_view == 'cart.html'                 # render đúng template

    # 3) Xóa sản phẩm khỏi giỏ
    body_rem = urlencode({'product_id': '5'}).encode()
    req_rem = fake_request(method='POST', path='/cart/remove', body=body_rem, cookies={'csrf_token': 'fixed-token'}, user=user)
    status_rem, headers_rem, _ = remove(req_rem)
    assert status_rem.startswith('303')
    assert storage[1] == {}                         # giỏ đã trống lại
