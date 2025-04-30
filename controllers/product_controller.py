# controllers/product_controller.py
from models import Product
from utils.csrf import gen_csrf_token, verify_csrf
from utils.template_engine import render_template
from urllib.parse import parse_qs
from sessions.session_manager import get_session
from controllers.auth_controller import parse_cookies

# Helpers
def _get_cart_count(request):
    # Lấy session_id từ header “Cookie”
    raw = request.headers.get('Cookie', '')
    cookies = parse_cookies(raw)
    sid = cookies.get('session_id')
    sess = get_session(sid) or {}
    return sum(sess.get('cart', {}).values())

# GET /product
def index(request):
    products   = Product.all()
    csrf       = gen_csrf_token()
    cart_count = _get_cart_count(request)

    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Set-Cookie',    f'csrf_token={csrf}; Path=/; HttpOnly; SameSite=Lax')
    ]
    html = render_template('index.html', {
        'products':   products,
        'csrf_token': csrf,
        'cart_count': cart_count
    }, request=request)
    return '200 OK', headers, html

# GET /product/<id>
def detail(request):
    pid = request.params.get('product_id')
    try:
        product_id = int(pid)
    except (TypeError, ValueError):
        return '400 Bad Request', [('Content-Type', 'text/plain')], 'Invalid product ID'

    p = Product.find_by_id(product_id)
    if not p:
        return '404 Not Found', [('Content-Type', 'text/plain')], 'Product not found'

    csrf       = gen_csrf_token()
    cart_count = _get_cart_count(request)
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Set-Cookie',    f'csrf_token={csrf}; Path=/; HttpOnly; SameSite=Lax')
    ]
    html = render_template('product_detail.html', {
        'product':    p,
        'csrf_token': csrf,
        'cart_count': cart_count
    }, request=request)
    return '200 OK', headers, html

# GET /product/new and /product/<id>/edit
def form(request):
    if not getattr(request, 'user', None) or not request.user.is_admin:
        return '303 See Other', [('Location', '/login')], ''

    pid = request.params.get('product_id')
    product = None
    if pid:
        try:
            product = Product.find_by_id(int(pid))
        except ValueError:
            pass

    if product:
        action_url   = f"/product/{product.product_id}/edit"
        submit_label = "Cập nhật"
    else:
        action_url   = "/product/create"
        submit_label = "Tạo mới"

    csrf = gen_csrf_token()
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Set-Cookie',    f'csrf_token={csrf}; Path=/; HttpOnly; SameSite=Lax')
    ]
    html = render_template('product_form.html', {
        'product':      product or {},
        'action_url':   action_url,
        'submit_label': submit_label,
        'csrf_token':   csrf
    }, request=request)
    return '200 OK', headers, html

# POST /product/create
def create(request):
    if not getattr(request, 'user', None) or not request.user.is_admin:
        return '303 See Other', [('Location', '/login')], ''
    if not verify_csrf(request):
        return '403 Forbidden', [], 'CSRF token không hợp lệ.'

    data = parse_qs(request.body)
    name  = data.get('name', [''])[0]
    try:
        price = float(data.get('price', [''])[0])
    except (ValueError, TypeError):
        price = 0
    try:
        stock = int(data.get('stock', [''])[0])
    except (ValueError, TypeError):
        stock = 0
    desc  = data.get('decription', [''])[0]
    image = data.get('image_url', [''])[0]

    if not name or price <= 0:
        token = parse_qs(request.headers.get('Cookie','')).get('csrf_token',[''])[0]
        html = render_template('product_form.html', {
            'product':      {},
            'action_url':   '/product/create',
            'submit_label': 'Tạo mới',
            'csrf_token':   token,
            'error':        'Tên và giá phải hợp lệ.'
        }, request=request)
        return '400 Bad Request', [('Content-Type','text/html; charset=utf-8')], html

    p = Product.create(
        name       = name,
        price      = price,
        stock      = stock,
        decription = desc,
        image_url  = image
    )
    return '303 See Other', [('Location', f'/product/{p.product_id}')], ''

# POST /product/<id>/edit
def update(request):
    if not getattr(request, 'user', None) or not request.user.is_admin:
        return '303 See Other', [('Location', '/login')], ''
    if not verify_csrf(request):
        return '403 Forbidden', [], 'CSRF token không hợp lệ.'

    pid = request.params.get('product_id')
    try:
        product_id = int(pid)
    except (TypeError, ValueError):
        return '400 Bad Request', [('Content-Type','text/plain')], 'Invalid product ID'

    p = Product.find_by_id(product_id)
    if not p:
        return '404 Not Found', [('Content-Type','text/plain')], 'Product not found'

    data = parse_qs(request.body)
    p.name       = data.get('name', [''])[0]
    try:
        p.price = float(data.get('price', [''])[0])
    except (ValueError, TypeError):
        p.price = 0
    try:
        p.stock = int(data.get('stock', [''])[0])
    except (ValueError, TypeError):
        p.stock = 0
    p.decription = data.get('decription', [''])[0]
    p.image_url  = data.get('image_url', [''])[0]
    p.update()

    return '303 See Other', [('Location', f'/product/{product_id}')], ''

# POST /product/<id>/delete
def delete(request):
    if not getattr(request, 'user', None) or not request.user.is_admin:
        return '303 See Other', [('Location', '/login')], ''
    if not verify_csrf(request):
        return '403 Forbidden', [], 'CSRF token không hợp lệ.'

    pid = request.params.get('product_id')
    try:
        product_id = int(pid)
    except (TypeError, ValueError):
        return '400 Bad Request', [('Content-Type','text/plain')], 'Invalid product ID'

    p = Product.find_by_id(product_id)
    if p:
        p.delete()
    return '303 See Other', [('Location', '/product')], ''
