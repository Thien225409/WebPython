from urllib.parse import parse_qs
from models.users import User
from utils.template_engine import render_template
from sessions.session_manager import create_session, delete_session, get_session

# Đăng kí người dùng 
def register(request):
    if request.method == 'POST':
        data = parse_qs(request.body)
        username = data.get('username', [''])[0]
        password = data.get('password', [''])[0]
        
        # Kiểm tra nếu user đã tồn tại
        try:
            user = User.register(username, password)
            return '303 See Other', [('Location', '/login')], ''
        except ValueError as e:
            html = render_template('register.html', {'error': str(e)})
            return '400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')], html
    
    # GET: hiển thị form
    html = render_template('register.html', {})
    return '200 OK', [('Content-Type', 'text/html; charset=utf-8')], html
# GET & POST /login
def login(request):
    if request.method == 'POST':
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
        html = render_template('login.html', {'error': 'Tên đăng nhập hoặc mật khẩu không đúng.'})
        return '400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')], html
    
    html = render_template('login.html', {})
    return '200 OK', [('Content-Type', 'text/html; charset=utf-8')], html

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