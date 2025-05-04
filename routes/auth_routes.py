from routes.router import add_route
import controllers.auth_controller as auth

# Đăng kí các đường dẫn
add_route('GET',  r'^/register$',        auth.register)
add_route('POST', r'^/register$',        auth.register)
add_route('GET',  r'^/forgot-password$', auth.forgot_password)
add_route('POST', r'^/forgot-password$', auth.forgot_password)
add_route('GET',  r'^/reset-password$',  auth.reset_password)
add_route('POST', r'^/reset-password$',  auth.reset_password)
add_route('GET',  r'^/login$',           auth.login)
add_route('POST', r'^/login$',           auth.login)
add_route('GET',  r'^/logout$',          auth.logout)
