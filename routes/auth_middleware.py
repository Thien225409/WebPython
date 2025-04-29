def require_auth(handler):
    """
    Decorator đảm bảo chỉ user đã login mới được phép gọi handler.
    Nếu chưa có session['user_id'], sẽ redirect về /login.
    """
    def wrapped(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return '303 See Other', [('Location', '/login')], ''
        return handler(request, *args, **kwargs)
    return wrapped