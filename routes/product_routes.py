# routes/product_routes.py
from routes.router import add_route
import controllers.product_controller as ctrl

# Lấy decorator từ auth_middleware
from routes.auth_middleware import require_auth

id_pat = r'(?P<product_id>\d+)'

# Chỉ index và detail là công khai
add_route('GET',  rf'^/product$',               ctrl.index)
add_route('GET',  rf'^/product/{id_pat}$',      ctrl.detail)

# Các route tạo/sửa/xóa sản phẩm buộc phải login
add_route('GET',  rf'^/product/new$',            require_auth(ctrl.form))
add_route('POST', rf'^/product/create$',         require_auth(ctrl.create))
add_route('GET',  rf'^/product/{id_pat}/edit$',  require_auth(ctrl.form))
add_route('POST', rf'^/product/{id_pat}/edit$',  require_auth(ctrl.update))
add_route('POST', rf'^/product/{id_pat}/delete$',require_auth(ctrl.delete))
