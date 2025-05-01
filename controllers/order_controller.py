from models.product import Product
from utils.csrf import gen_csrf_token, verify_csrf
from utils.template_engine import render_template
from models.order import Order
from models.cart import Cart
def list(request):
    """
    Hiển thị danh sách đơn hàng của user.
    """
    if not request.user:
        return '303 See Other', [('Location', '/login')], 'Hiện bạn chưa đăng nhập.'

    orders = Order.list_by_user(request.user.user_id)
    csrf = gen_csrf_token()
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Set-Cookie', f'csrf_token={csrf}; Path=/; HttpOnly; SameSite=Lax')
    ]
    body = render_template(
        'orders.html', 
        {
            'orders': orders,
            'csrf_token': csrf
        }, 
        request=request
    )
    return '200 OK', headers, body

def checkout(request):
    """
    Xử lý POST /checkout: chuyển items từ Cart sang Order.
    """
    if request.method != 'POST':
        return '303 See Other', [('Location', '/orders')], 'Hiện bạn chưa đăng nhập.'
    if not request.user:
        return '303 See Other', [('Location', '/login')], 'Hiện bạn chưa đăng nhập.'
    if not verify_csrf(request):
        return '403 Forbidden', [], 'CSRF token không hợp lệ.'
    user_id = request.user.user_id
    # Lấy giỏ hàng
    raw_items = Cart.get_items(user_id)
    items = []
    total = 0
    for pid, qty in raw_items.items():
        p = Product.find_by_id(pid)
        if p:
            items.append(
                {
                    'product': p,
                    'qty': qty
                }
            )
            total += p.price * qty
    # Tạo đơn hàng và xóa sản phẩm vừa thực hiện thanh toán
    Order.create(user_id, items, total)
    for pid in raw_items.keys():
        Cart.remove_item(user_id, pid)
    return '303 See Other', [('Location', '/orders')], 'Hiện bạn chưa đăng nhập.'
    