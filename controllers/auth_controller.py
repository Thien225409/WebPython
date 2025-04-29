from urllib.parse import parse_qs
from utils.csrf import gen_csrf_token, verify_csrf
from models.users import User
from utils.template_engine import render_template
from sessions.session_manager import create_session, delete_session, get_session

def render_form(template, request):
    token = gen_csrf_token()
    html = render_template(template, {'csrf_token': token})
    return '200 OK', [
        ('Content-Type','text/html; charset=utf-8'),
        ('Set-Cookie', f'csrf_token={token}; Path=/')
    ], html

# Đăng kí người dùng 
def register(request):
    # GET
    if request.method == 'GET':
        return render_form('register.html', request)
    # POST
    if not verify_csrf(request):
        return '403 Forbidden', [], 'CSRF token không hợp lệ.'
    
    data = parse_qs(request.body)
    username = data.get('username', [''])[0]
    password = data.get('password', [''])[0]
    
    # Kiểm tra nếu user đã tồn tại
    try:
        User.register(username, password)
        return '303 See Other', [('Location', '/login')], ''
    except ValueError as e:
        # giữ lại csrf_token cũ để render lại
        token = parse_qs(request.headers.get('Cookies', ''))['csrf_token']
        html = render_template('register.html', {
            'error': str(e),
            'csrf_token': token
        })
        
        return '400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')], html
# GET & POST /login
def login(request):
    if request.method == 'GET':
        return render_form('login.html', request)
    
    # POST
    if not verify_csrf(request):
        return '403 Forbidden', [], 'CSRF token không hợp lệ.'
    
    data = parse_qs(request.body)
    username = data.get('username', [''])[0]
    password = data.get('password', [''])[0]
    
    # Truy vaan trong co so du lieu
    user = User.find_by_username(username)
    if user and user.check_password(password):
        # Tạo session và lưu session_id vào cookie
        sid = create_session(user.user_id)
        headers = [
            ('Set-Cookie', f'session_id={sid}; Path=/; HttpOnly'),
            ('Location','/')
        ]
        return '303 See Other', headers, ''
    # Sai thông tin: trả lại form với lỗi
    token = parse_qs(request.headers.get('Cookie',''))['csrf_token']
    html = render_template('login.html', {
        'error': 'Tên đăng nhập hoặc mật khẩu không đúng.',
        'csrf_token': token
    })
    return '400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')], html

# Phân tích header Cookie thành dict 
def parse_cookies(cookie_header: str) -> dict:
    """
    Chuyển chuỗi Cookie header thành dict:
    "k1=v1; k2=v2" -> {"k1": "v1", "k2": "v2"}
    """
    cookies = {}
    for pair in cookie_header.split('; '):
        if '=' in pair:
            name, value = pair.split('=', 1)
            cookies[name] = value
    return cookies
# GET /logout
def logout(request):
    # 1. Lấy header "Cookie" (nếu không có thì trả về chuỗi rỗng)
    raw_cookies = request.headers.get('Cookie', '')

    # 2. Phân tích thành dict để dễ truy cập
    cookies = parse_cookies(raw_cookies)
    session_id = cookies.get('session_id')

    # 3. Nếu có session_id thì xóa khỏi server
    if session_id:
        delete_session(session_id)

    # 4. Chuẩn bị header trả về:
    #    - Xóa cookie trên trình duyệt (Max-Age=0)
    #    - Chuyển hướng về trang /login bằng 303 See Other
    response_headers = [
        ('Set-Cookie',  'session_id=; Path=/; Max-Age=0; HttpOnly'),
        ('Location',    '/login'),
    ]

    # 5. Trả về status, headers và body rỗng
    return '303 See Other', response_headers, ''