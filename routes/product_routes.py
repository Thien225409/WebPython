# routes/product_routes.py
from routes.router import add_route
import controllers.product_controller as ctrl

id_pat    = r'(?P<product_id>\d+)'

# List, Form, Create, Detail, Update, Delete
add_route('GET',  rf'^/product$',                 ctrl.index)
add_route('GET',  rf'^/product/new$',             ctrl.form)
add_route('POST', rf'^/product/create$',          ctrl.create)
add_route('GET',  rf'^/product/{id_pat}$',        ctrl.detail)
add_route('GET',  rf'^/product/{id_pat}/edit$',   ctrl.form)
add_route('POST', rf'^/product/{id_pat}/edit$',   ctrl.update)
add_route('POST', rf'^/product/{id_pat}/delete$', ctrl.delete)
