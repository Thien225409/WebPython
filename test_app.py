import uuid
import re
import pytest
import requests
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"

def extract_csrf(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, "Không tìm thấy csrf_token trong form"
    return m.group(1)

@pytest.fixture
def admin_session():
    s = requests.Session()
    # 1) Đăng ký admin (nếu chưa có thì thành công, nếu đã có thì vẫn redirect)
    r = s.get(urljoin(BASE_URL, "/register"))
    csrf = extract_csrf(r.text)
    s.post(
        urljoin(BASE_URL, "/register"),
        data={"username": "admin", "password": "Hungblack99@", "csrf_token": csrf},
        allow_redirects=False
    )
    # 2) Đăng nhập admin
    r2 = s.get(urljoin(BASE_URL, "/login"))
    csrf2 = extract_csrf(r2.text)
    r3 = s.post(
        urljoin(BASE_URL, "/login"),
        data={"username": "admin", "password": "Hungblack99@", "csrf_token": csrf2},
        allow_redirects=False
    )
    assert r3.status_code == 303 and r3.headers["Location"] == "/product"
    return s

@pytest.fixture
def user_session():
    s = requests.Session()
    # Tạo và login user random
    username = f"user_{uuid.uuid4().hex[:8]}"
    password = "userpass"
    # register
    r = s.get(urljoin(BASE_URL, "/register"))
    csrf = extract_csrf(r.text)
    s.post(
        urljoin(BASE_URL, "/register"),
        data={"username": username, "password": password, "csrf_token": csrf},
        allow_redirects=False
    )
    # login
    r2 = s.get(urljoin(BASE_URL, "/login"))
    csrf2 = extract_csrf(r2.text)
    r3 = s.post(
        urljoin(BASE_URL, "/login"),
        data={"username": username, "password": password, "csrf_token": csrf2},
        allow_redirects=False
    )
    assert r3.status_code == 303 and r3.headers["Location"] == "/product"
    return s

def test_non_admin_cannot_access_crud(user_session):
    s = user_session
    # GET form new
    r = s.get(urljoin(BASE_URL, "/product/new"), allow_redirects=False)
    assert r.status_code == 303 and r.headers["Location"] == "/login"
    # POST create
    r2 = s.post(urljoin(BASE_URL, "/product/create"), data={}, allow_redirects=False)
    assert r2.status_code == 303 and r2.headers["Location"] == "/login"
    # GET edit
    r3 = s.get(urljoin(BASE_URL, "/product/1/edit"), allow_redirects=False)
    assert r3.status_code == 303 and r3.headers["Location"] == "/login"
    # POST update
    r4 = s.post(urljoin(BASE_URL, "/product/1/edit"), data={}, allow_redirects=False)
    assert r4.status_code == 303 and r4.headers["Location"] == "/login"
    # POST delete
    r5 = s.post(urljoin(BASE_URL, "/product/1/delete"), data={}, allow_redirects=False)
    assert r5.status_code == 303 and r5.headers["Location"] == "/login"

def test_admin_can_full_crud(admin_session):
    s = admin_session

    # 1) GET /product/new → 200 + CSRF
    r = s.get(urljoin(BASE_URL, "/product/new"))
    assert r.status_code == 200
    csrf1 = extract_csrf(r.text)

    # 2) POST /product/create → 303 → /product/{id}
    name = f"P_{uuid.uuid4().hex[:6]}"
    r2 = s.post(
        urljoin(BASE_URL, "/product/create"),
        data={
            "name": name,
            "price": "123.45",
            "stock": "7",
            "description": "desc",
            "image_url": "",
            "csrf_token": csrf1
        },
        allow_redirects=False
    )
    assert r2.status_code == 303
    loc = r2.headers["Location"]
    assert loc.startswith("/product/")
    pid = loc.split("/")[-1]

    # 3) GET /product/{pid} → 200 + xem đúng tên
    r3 = s.get(urljoin(BASE_URL, f"/product/{pid}"))
    assert r3.status_code == 200
    assert name in r3.text

    # 4) GET /product/{pid}/edit → 200 + CSRF
    r4 = s.get(urljoin(BASE_URL, f"/product/{pid}/edit"))
    assert r4.status_code == 200
    csrf2 = extract_csrf(r4.text)

    # 5) POST update → 303 → /product/{pid}
    new_name = name + "_E"
    r5 = s.post(
        urljoin(BASE_URL, f"/product/{pid}/edit"),
        data={
            "name": new_name,
            "price": "543.21",
            "stock": "3",
            "description": "edited",
            "image_url": "",
            "csrf_token": csrf2
        },
        allow_redirects=False
    )
    assert r5.status_code == 303
    assert r5.headers["Location"] == f"/product/{pid}"

    # 6) GET detail again → 200 + tên mới
    r6 = s.get(urljoin(BASE_URL, f"/product/{pid}"))
    assert new_name in r6.text

    # 7) POST delete → 303 → /product
    r7 = s.post(
        urljoin(BASE_URL, f"/product/{pid}/delete"),
        data={"csrf_token": csrf2},
        allow_redirects=False
    )
    assert r7.status_code == 303
    assert r7.headers["Location"] == "/product"

    # 8) GET list → không thấy sản phẩm
    r8 = s.get(urljoin(BASE_URL, "/product"))
    assert new_name not in r8.text
