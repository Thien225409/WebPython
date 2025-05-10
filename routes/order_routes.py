from routes.router import add_route
from routes.auth_middleware import require_auth
import controllers.order_controller as ctrl

# Xem danh sách đơn hàng
add_route('GET',  r'^/orders$',    require_auth(ctrl.list))
# Thanh toán (checkout)
add_route('POST', r'^/checkout$', require_auth(ctrl.checkout))
# Hiển thị trang thanh toán QR
add_route('GET',  r'^/checkout$', require_auth(ctrl.checkout_view))