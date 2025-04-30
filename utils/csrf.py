import uuid

def gen_csrf_token():
    """
    Server: sinh csrf_token là một string sinh ngẫu nhiên
    """
    return str(uuid.uuid4())

def verify_csrf(request):
    from urllib.parse import parse_qs
    from controllers.auth_controller import parse_cookies

    """
    Server: Thực hiện so sánh csrf_token trong cookies với csrf_token trong form của client gửi
    """
    # Lấy token trong body
    form = parse_qs(request.body) # Lấy body trong request chuyển thành dạng dict
    form_token = form.get('csrf_token', [''])[0] # Tách csrf_token ra
    
    # Nếu không có csrf_token trong form, trả về False
    if not form_token:
        return False
    
    # Lấy cookies trong header
    cookies = parse_cookies(request.headers.get('Cookie', '')) # Lấy cookies dạng dict
    cookie_token = cookies.get('csrf_token', '')

    if not cookie_token:
        # Nếu không có csrf_token trong cookies, trả về False
        return False

    # So sánh
    return cookie_token == form_token

    