import uuid

def gen_csrf_token():
    return str(uuid.uuid4())

def verify_csrf(request):
    from urllib.parse import parse_qs
    from controllers.auth_controller import parse_cookies
    """"
    Thực hiện so sánh csrf_token trong cookies với csrf_token trong form của client gửi
    """
    # Lấy token trong body
    form = parse_qs(request.body)
    form_token = form.get('csrf_token', [''])[0]
    # Lấy cookies trong header
    cookies = parse_cookies(request.headers.get('Cookie', ''))
    # So sánh
    return cookies.get('csrf_token') == form_token
    