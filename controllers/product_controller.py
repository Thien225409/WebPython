# controllers/product_controller.py
from models import Product
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
    pid = request.params.get('product_id')
    product = None
    if pid:
        try:
            product = Product.find_by_id(int(pid))
        except ValueError:
            pass
    
    # Xác định URL form và label
    if product:
        action_url = f"/product/{product.product_id}/edit"
        submit_label = "Cập nhật"
    else:
        action_url = "/product/create"
        submit_label = "Tạo mới"
    html = render_template('product_form.html', {
        'product': product,
        'action_url': action_url,
        'submit_label': submit_label
    })
    return '200 OK', [('Content-Type', 'text/html; charset=utf-8')], html

# POST /product/create
def create(request):
    data       = parse_qs(request.body)
    name       = data.get('name', [''])[0]
    price      = float(data.get('price', ['0'])[0])
    stock      = int(data.get('stock', ['0'])[0])
    decription = data.get('decription', [''])[0]
    image_url  = data.get('image_url', [''])[0]
    
    # Validation
    if not name or price <= 0:
        html = render_template('product_form.html', {
            'product': None,
            'action_url': '/product/create',
            'submit_label': 'Tạo mới',
            'error': 'Tên và giá phải hợp lệ.'
        })
    p = Product.create(
        name       = name,
        price      = price,
        stock      = stock,
        decription = decription,
        image_url  = image_url
    )
    return '303 See Other', [('Location', f'/product/{p.product_id}')], ''
    # return '303 See Other', [('Location', '/product')], ''

# POST /product/<product_id>/edit
def update(request):
    pid = request.params.get('product_id')
    try:
        product_id = int(pid)
    except (TypeError, ValueError):
        return '400 Bad Request', [('Content-Type', 'text/plain')], 'Invalid product ID'

    data = parse_qs(request.body)
    p = Product.find_by_id(product_id)
    if not p:
        return '404 Not Found', [('Content-Type', 'text/plain')], 'Product not found'

    p.name       = data.get('name', [''])[0]
    p.price      = float(data.get('price', ['0'])[0])
    p.stock      = int(data.get('stock', ['0'])[0])
    p.decription = data.get('decription', [''])[0]
    p.image_url  = data.get('image_url', [''])[0]
    p.update()

    return '303 See Other', [('Location', f'/product/{product_id}')], ''

# POST /product/<product_id>/delete
def delete(request):
    pid = request.params.get('product_id')
    try:
        product_id = int(pid)
    except (TypeError, ValueError):
        return '400 Bad Request', [('Content-Type', 'text/plain')], 'Invalid product ID'

    p = Product.find_by_id(product_id)
    if p:
        p.delete()
    return '303 See Other', [('Location', '/')], ''
