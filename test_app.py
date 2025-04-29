import re
import pytest
import requests
from urllib.parse import urljoin, parse_qs

BASE_URL = "http://localhost:8000"

@pytest.fixture
def session():
    return requests.Session()

def extract_csrf(response):
    # Tìm giá trị của hidden input name="csrf_token" trong HTML
    m = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    assert m, "Không tìm thấy csrf_token trong form"
    return m.group(1)

def test_public_product_list_and_detail(session):
    # 1. GET /product → 200 OK
    r = session.get(urljoin(BASE_URL, "/product"))
    assert r.status_code == 200

    # 2. GET /product/1 → 200 OK (giả định có product_id=1)
    r2 = session.get(urljoin(BASE_URL, "/product/1"))
    assert r2.status_code == 200

def test_register_login_logout_flow(session):
    # 3. GET /register → form với CSRF
    r = session.get(urljoin(BASE_URL, "/register"))
    assert r.status_code == 200
    csrf = extract_csrf(r)

    # 4. POST /register (thiếu CSRF) → 403
    r_bad = session.post(urljoin(BASE_URL, "/register"), data={"username":"u1","password":"p1"})
    assert r_bad.status_code == 403

    # 5. POST /register (có CSRF) → 303 redirect
    r2 = session.post(
        urljoin(BASE_URL, "/register"),
        data={"username":"testuser","password":"secret","csrf_token": csrf},
        allow_redirects=False
    )
    assert r2.status_code == 303
    assert r2.headers["Location"] == "/login"

    # 6. GET /login và lấy CSRF
    r3 = session.get(urljoin(BASE_URL, "/login"))
    assert r3.status_code == 200
    csrf2 = extract_csrf(r3)

    # 7. POST /login (có CSRF) → 303 redirect home
    r4 = session.post(
        urljoin(BASE_URL, "/login"),
        data={"username":"testuser","password":"secret","csrf_token": csrf2},
        allow_redirects=False
    )
    assert r4.status_code == 303
    assert r4.headers["Location"] == "/"

    # 8. GET /logout → 303 redirect /login
    r5 = session.get(urljoin(BASE_URL, "/logout"), allow_redirects=False)
    assert r5.status_code == 303
    assert r5.headers["Location"] == "/login"

def test_protected_product_crud_requires_login(session):
    # A. Unauthenticated: GET new → redirect /login
    r = session.get(urljoin(BASE_URL, "/product/new"), allow_redirects=False)
    assert r.status_code == 303 and r.headers["Location"] == "/login"

    # B. Unauthenticated: POST create → redirect /login
    r2 = session.post(urljoin(BASE_URL, "/product/create"), allow_redirects=False)
    assert r2.status_code == 303 and r2.headers["Location"] == "/login"

def test_product_crud_flow(session):
    # Đăng ký + login
    r = session.get(urljoin(BASE_URL, "/register"))
    csrf = extract_csrf(r)
    session.post(urljoin(BASE_URL, "/register"), data={"username":"cruduser","password":"pwd","csrf_token": csrf})
    r = session.get(urljoin(BASE_URL, "/login"))
    csrf = extract_csrf(r)
    session.post(urljoin(BASE_URL, "/login"), data={"username":"cruduser","password":"pwd","csrf_token": csrf})

    # GET /product/new → có form + CSRF
    r = session.get(urljoin(BASE_URL, "/product/new"))
    assert r.status_code == 200
    csrf = extract_csrf(r)

    # POST /product/create với CSRF → redirect về /product
    r2 = session.post(
        urljoin(BASE_URL, "/product/create"),
        data={"name":"Thịt ba chỉ","price":"100000","stock":"5","category_id":"1","description":"Test","csrf_token": csrf},
        allow_redirects=False
    )
    assert r2.status_code == 303 and r2.headers["Location"] == "/product"

    # Giả định sản phẩm mới có ID= last, lấy detail
    # Bạn có thể parse id từ redirect URL hoặc query DB trực tiếp
    # Ví dụ tạm test GET /product/2
    r3 = session.get(urljoin(BASE_URL, "/product/2"))
    assert r3.status_code == 200

    # Test Edit
    r4 = session.get(urljoin(BASE_URL, "/product/2/edit"))
    csrf = extract_csrf(r4)
    r5 = session.post(
        urljoin(BASE_URL, "/product/2/edit"),
        data={"name":"Ba chỉ sửa","price":"110000","stock":"10","category_id":"1","description":"Sửa","csrf_token": csrf},
        allow_redirects=False
    )
    assert r5.status_code == 303

    # Test Delete
    # Lấy CSRF mới nếu cần form delete, hoặc reuse cookie
    r6 = session.post(
        urljoin(BASE_URL, "/product/2/delete"),
        data={"csrf_token": csrf},
        allow_redirects=False
    )
    assert r6.status_code == 303

    # Đăng xuất
    session.get(urljoin(BASE_URL, "/logout"))
