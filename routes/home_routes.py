# routes/home_routes.py
from routes.router import add_route

# Chuyển hướng root → /product
def home(request):
    return '303 See Other', [('Location', '/product')], ''

add_route('GET', r'^/$', home)
