import pytest
from urllib.parse import urlencode
from controllers import product_controller as pc
from models.users import User
from models import Product
from utils.conftest import fake_request

@pytest.fixture
def admin_user():
    user = User.find_by_username('admin')
    user.is_admin = True  # ✅ giả lập quyền admin
    return user

@pytest.fixture
def csrf_token():
    return 'valid_csrf'

# ✅ Test tạo sản phẩm thành công
def test_create_product_success(admin_user, csrf_token):
    body = urlencode({
        'name': 'Thịt ba rọi',
        'price': '180000',
        'stock': '10',
        'decription': 'Ngon mềm, thích hợp nướng',
        'image_url': '/public/images/ba_roi.png',
        'csrf_token': csrf_token
    })
    cookies = {'csrf_token': csrf_token}

    req = fake_request(
        method='POST',
        path='/product/create',
        body=body,
        cookies=cookies,
        user=admin_user
    )

    status, headers, _ = pc.create(req)
    
    print("HEADERS:", headers)
    assert status.startswith('303')
    assert any(h[0] == 'Location' and '/product/' in h[1] for h in headers)

# ❌ Test CSRF không hợp lệ
def test_create_product_csrf_fail(admin_user):
    body = urlencode({
        'name': 'Thịt bò',
        'price': '250000',
        'stock': '5'
    })

    req = fake_request(
        method='POST',
        path='/product/create',
        body=body,
        cookies={},  # Không có csrf_token
        user=admin_user
    )

    status, _, body = pc.create(req)
    assert status == '403 Forbidden'
    assert 'CSRF' in body

# ❌ Test tạo sản phẩm thiếu tên/giá
def test_create_product_invalid_data(admin_user, csrf_token):
    body = urlencode({
        'name': '',
        'price': '0',
        'stock': '10',
        'csrf_token': csrf_token
    })
    cookies = {'csrf_token': csrf_token}

    req = fake_request(
        method='POST',
        path='/product/create',
        body=body,
        cookies=cookies,
        user=admin_user
    )

    status, headers, html = pc.create(req)

    assert status.startswith('400')
    assert 'Tên và giá phải hợp lệ' in html

# ✅ Test detail sản phẩm hợp lệ
def test_product_detail_ok():
    # Tạo sản phẩm trước (hoặc đảm bảo ID 1 tồn tại)
    p = Product.create('Test sản phẩm', 123000, 1, 'Mô tả test', '/public/images/test.png')

    req = fake_request(
        method='GET',
        path=f'/product/{p.product_id}',
        params={'product_id': str(p.product_id)}
    )

    status, headers, body = pc.detail(req)

    assert status == '200 OK'
    assert p.name in body

# ❌ Test detail sản phẩm không tồn tại
def test_product_detail_not_found():
    req = fake_request(
        method='GET',
        path='/product/999999',
        params={'product_id': '999999'}
    )

    status, _, body = pc.detail(req)

    assert status == '404 Not Found'
    assert 'Product not found' in body
