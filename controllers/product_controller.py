# controllers/product_controller.py
from models import Product
from utils.csrf import gen_csrf_token, verify_csrf
from utils.template_engine import render_template
from urllib.parse import parse_qs

# GET /product
# List all products

def index(request):
    products = Product.all()
    html = render_template('index.html', {'products': products})
    return '200 OK', [('Content-Type', 'text/html; charset=utf-8')], html

# GET /product/<product_id>
def detail(request):
    pid = request.params.get('product_id')
    try:
        product_id = int(pid)
    except (TypeError, ValueError):
        return '400 Bad Request', [('Content-Type', 'text/plain')], 'Invalid product ID'

    p = Product.find_by_id(product_id)
    if not p:
        return '404 Not Found', [('Content-Type', 'text/plain')], 'Product not found'

    html = render_template('product_detail.html', {'product': p})
    return '200 OK', [('Content-Type', 'text/html; charset=utf-8')], html

# GET /product/new and GET /product/<product_id>/edit
def form(request):
    """
    GET /product/new
    GET /product/<id>/edit
    Admin-only: hiện form thêm/sửa.
    """
    # Authorization: chỉ admin mới vào được
    if not getattr(request, 'user', None) or not getattr(request.user, 'is_admin', False):
        return '303 See Other', [('Location', '/login')], ''

    pid = request.params.get('product_id')
    product = None
    if pid:
        try:
            product = Product.find_by_id(int(pid))
        except ValueError:
            pass

    # Xác định URL và label
    if product:
        action_url  = f"/product/{product.product_id}/edit"
        submit_label = "Cập nhật"
    else:
        action_url  = "/product/create"
        submit_label = "Tạo mới"

    # GET: sinh CSRF token, set cookie, render form
    token = gen_csrf_token()
    html = render_template('product_form.html', {
        'product':       product or {},
        'action_url':    action_url,
        'submit_label':  submit_label,
        'csrf_token':    token
    })
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Set-Cookie',   f'csrf_token={token}; Path=/; HttpOnly; SameSite=Lax')
    ]
    return '200 OK', headers, html
# POST /product/create
def create(request):
    """
    POST /product/create
    Admin-only + CSRF: tạo mới sản phẩm, redirect về danh sách.
    """
    if not getattr(request, 'user', None) or not getattr(request.user, 'is_admin', False):
        return '303 See Other', [('Location', '/login')], ''
    if not verify_csrf(request):
        return '403 Forbidden', [], 'CSRF token không hợp lệ.'

    data = parse_qs(request.body)
    name    = data.get('name', [''])[0]
    price   = float(data.get('price', ['0'])[0] or 0)
    stock   = int(data.get('stock', ['0'])[0] or 0)
    desc    = data.get('description', [''])[0]
    image   = data.get('image_url', [''])[0]

    # Simple validation
    try:
        price = float(data.get('price', [''])[0])
    except ValueError:
        price = 0
    if not name or price <= 0:
        # Nếu lỗi, render lại form cùng error
        html = render_template('product_form.html', {
            'product':      {},
            'action_url':   '/product/create',
            'submit_label': 'Tạo mới',
            'csrf_token':   parse_qs(request.headers.get('Cookie','')).get('csrf_token','')[0],
            'error':        'Tên và giá phải hợp lệ.'
        })
        return '400 Bad Request', [('Content-Type','text/html; charset=utf-8')], html

    p = Product.create(
        name        = name,
        price       = price,
        stock       = stock,
        decription  = desc,
        image_url   = image
    )
    return '303 See Other', [('Location', f'/product/{p.product_id}')], ''

# POST /product/<product_id>/edit
def update(request):
    """
    POST /product/<id>/edit
    Admin-only + CSRF: cập nhật sản phẩm, redirect về detail.
    """
    if not getattr(request, 'user', None) or not getattr(request.user, 'is_admin', False):
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
    p.price      = float(data.get('price', ['0'])[0] or 0)
    p.stock      = int(data.get('stock', ['0'])[0] or 0)
    p.decription = data.get('description', [''])[0]
    p.image_url  = data.get('image_url', [''])[0]
    p.update()

    return '303 See Other', [('Location', f'/product/{product_id}')], ''
# POST /product/<product_id>/delete
def delete(request):
    """
    POST /product/<id>/delete
    Admin-only + CSRF: xóa sản phẩm, redirect về danh sách.
    """
    if not getattr(request, 'user', None) or not getattr(request.user, 'is_admin', False):
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
