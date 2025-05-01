from models.cart import Cart
from models.product import Product
from utils.csrf import gen_csrf_token, verify_csrf
from utils.template_engine import render_template
from urllib.parse import parse_qs
def view(request):
    """
    Hiển thị giỏ hàng của user hiện tại.
    Trả về HTML đã render với cart_items và cart_total.
    """
    user = request.user
    # Lấy dict {product_id: quantity}
    raw_items = Cart.get_items(user.user_id)
    items = []
    total = 0
    # Duyệt từng dict
    for pid, qty in raw_items.items():
        p = Product.find_by_id(pid)
        # Nếu có có sản phẩm này
        if p:
            subtotal = p.price * qty
            total += subtotal
            items.append(
                {
                    'product': p,
                    'qty': qty,
                    'subtotal': subtotal
                }
            )
             
    # Sinh CSRF token cho view
    csrf = gen_csrf_token()
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Set-Cookie', f'csrf_token={csrf}; Path=/; HttpOnly; SameSite=Lax')
    ]
    body = render_template(
        'cart.html', 
        {
            'cart_items': items,
            'cart_total': total,
            'csrf_token': csrf
        },
        request=request
    )
    return '200 OK', headers, body

def add(request):
    """
    Xử lý POST /cart/add: thêm 1 sản phẩm vào giỏ.
    Yêu cầu CSRF và user đã đăng nhập.
    """
    if request.method != 'POST':
        return '303 See Other', [('Location', '/cart')], ''
    if not request.user:
        # Thêm sản phẩm vào giỏ khi chưua đăng nhập thì chuyển người dùng đến trang đăng nhập
        return '303 See Other', [('Location', '/login')], 'Hiện bạn chưa đăng nhập.'
    if not verify_csrf(request):
        return '403 Forbidden', [], 'CSRF token không hợp lệ.'
    
    raw = request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body
    data = parse_qs(raw)
    pid = int(data.get('product_id', ['0'])[0])
    Cart.add_item(request.user.user_id, pid)
    return '303 See Other', [('Location', '/cart')], 'Thêm sản phẩm vào giỏ thành công.'

def remove(request):
    """
    Xử lý POST /cart/remove: xóa sản phẩm khỏi giỏ.
    """
    if not request.user:
        return '303 See Other', [('Location', '/login')], 'Hiện bạn chưa đăng nhập.'
    if not verify_csrf(request):
        return '403 Forbidden', [], 'CSRF token không hợp lệ.'
    raw = request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body
    data = parse_qs(raw)
    pid = int(data.get('product_id', ['0'])[0])
    Cart.remove_item(request.user.user_id, pid)
    return '303 See Other', [('Location', '/cart')], 'Xóa sản phẩm thành công.'

        