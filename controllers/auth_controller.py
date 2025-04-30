from urllib.parse import parse_qs
from utils.csrf import gen_csrf_token, verify_csrf
from models.users import User
from utils.template_engine import render_template
from sessions.session_manager import create_session, delete_session

def render_form(template: str, request) -> tuple:
    """
    Render form HTML với CSRF token mới và gắn cookie CSRF.

    Tham số:
        template (str): Tên file template (ví dụ 'login.html').
        request: đối tượng HTTP request.

    Trả về:
        status (str): Mã HTTP (ví dụ '200 OK').
        headers (list): Danh sách tuple header để thêm vào response.
        html (str): Nội dung HTML đã render.
    """
    token = gen_csrf_token()
    html = render_template(template, {'csrf_token': token}, request=request)
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Set-Cookie', f'csrf_token={token}; Path=/; HttpOnly; SameSite=Lax')
    ]
    return '200 OK', headers, html

# Đăng kí người dùng 
def register(request) -> tuple:
    """
    Xử lý đăng ký người dùng.

    - GET: Trả form đăng ký với CSRF token.
    - POST: Xác thực CSRF, lấy dữ liệu form, đăng ký User.

    Trả về:
        200 OK: Hiển thị form đăng ký.
        403 Forbidden: CSRF không hợp lệ.
        400 Bad Request: lỗi trùng tên, hiển thị lại form với thông báo.
        303 See Other: đăng ký thành công, redirect về /login.
    """
    # GET: hiển thị form
    if request.method == 'GET':
        return render_form('register.html', request)

    # POST: xác thực CSRF
    if not verify_csrf(request):
        return '403 Forbidden', [('Content-Type', 'text/plain; charset=utf-8')], 'CSRF token không hợp lệ.'

    form = parse_qs(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body)
    username = form.get('username', [''])[0]
    password = form.get('password', [''])[0]

    try:
        User.register(username, password)
        # Đăng ký thành công
    except ValueError:
        # Lỗi trùng tên: render lại form với thông báo lỗi
        raw_cookies = request.headers.get('Cookie', '')
        cookies = parse_cookies(raw_cookies)
        csrf_token = cookies.get('csrf_token','')
        html = render_template(
            'register.html',
            {'error': 'Tên đăng nhập đã tồn tại.', 'csrf_token': csrf_token},
            request=request
        )
        return '400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')], html

    # Thành công
    return '303 See Other', [('Location', '/login')], ''

# GET & POST /login
def login(request) -> tuple:
    """
    Xử lý đăng nhập người dùng.

    - GET: Trả form login với CSRF token.
    - POST: Xác thực CSRF, kiểm tra credentials, tạo session.

    Trả về:
        200 OK: Hiển thị form login.
        403 Forbidden: CSRF không hợp lệ.
        303 See Other: đăng nhập thành công, redirect về /product, kèm cookie.
        400 Bad Request: sai thông tin, hiển thị lại form với thông báo.
    """
    # GET: hiển thị form
    if request.method == 'GET':
        return render_form('login.html', request)

    # POST: xác thực CSRF
    if not verify_csrf(request):
        return '403 Forbidden', [('Content-Type', 'text/plain; charset=utf-8')], 'CSRF token không hợp lệ.'

    form = parse_qs(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body)
    username = form.get('username', [''])[0]
    password = form.get('password', [''])[0]

    user = User.find_by_username(username)
    if user and user.check_password(password):
        # Tạo session mới
        sid = create_session(user.user_id)
        # Tạo CSRF token mới cho phiên
        csrf_token = gen_csrf_token()

        headers = [
            ('Set-Cookie', f'session_id={sid}; Path=/; HttpOnly; SameSite=Lax'),
            ('Set-Cookie', f'csrf_token={csrf_token}; Path=/; HttpOnly; SameSite=Lax'),
            ('Location', '/product')
        ]
        return '303 See Other', headers, ''

    # Sai thông tin xác thực: trả lại form với lỗi
    raw_cookies = request.headers.get('Cookie', '')
    cookies = parse_cookies(raw_cookies)
    token = cookies.get('csrf_token', '')
    html = render_template(
        'login.html',
        {'error': 'Tên đăng nhập hoặc mật khẩu không đúng.','csrf_token': token},
        request=request
    )
    return '400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')], html

# Phân tích header Cookie thành dict 
def parse_cookies(cookie_header: str) -> dict:
    """
    Chuyển chuỗi Cookie header thành dict {name: value}.

    Ví dụ:
        "k1=v1; k2=v2" -> {'k1': 'v1', 'k2': 'v2'}
    """
    cookies = {}
    if not cookie_header:
        return cookies
    for pair in cookie_header.split(';'):
        if '=' in pair:
            name, value = pair.split('=', 1)
            cookies[name.strip()] = value.strip()
    return cookies
# GET /logout
def logout(request):
    """
    Đăng xuất user:
    - Xóa session trên server.
    - Xóa cookie session và csrf trên client.
    - Chuyển hướng về /login.

    Trả về:
        '303 See Other' kèm header xóa cookie và Location '/login'.
    """
    # 1. Lấy header "Cookie" (nếu không có thì trả về chuỗi rỗng)
    raw_cookies = request.headers.get('Cookie', '')

    # 2. Phân tích thành dict để dễ truy cập
    cookies = parse_cookies(raw_cookies)
    session_id = cookies.get('session_id')

    # 3. Nếu có session_id thì xóa
    if session_id:
        delete_session(session_id)

    # 4. Chuẩn bị header trả về:
    #    - Xóa cookie trên trình duyệt (Max-Age=0)
    #    - Chuyển hướng về trang /login bằng 303 See Other
    response_headers = [
        ('Set-Cookie', 'session_id=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax'),
        ('Set-Cookie', 'csrf_token=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax'),
        ('Location', '/login')
    ]
    return '303 See Other', response_headers, ''