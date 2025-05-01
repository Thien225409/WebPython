from routes.router import add_route
from routes.auth_middleware import require_auth
import controllers.cart_controller as ctrl

# Xem giỏ hàng
add_route('GET',  r'^/cart$',        require_auth(ctrl.view))
# Thêm sản phẩm vào giỏ
add_route('POST', r'^/cart/add$',    require_auth(ctrl.add))
# Xóa sản phẩm khỏi giỏ
add_route('POST', r'^/cart/remove$', require_auth(ctrl.remove))