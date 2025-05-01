from http.server import HTTPServer, BaseHTTPRequestHandler
from config import PORT
from urllib.parse import urlparse, parse_qs

from sessions.session_manager import get_session
from models.users import User
from controllers.auth_controller import parse_cookies

import routes.auth_routes
import routes.product_routes
import routes.static_routes
import routes.cart_routes
import routes.order_routes

from routes.router import ROUTES
class Request:
    def __init__(self, method, path, query, headers, body, params=None):
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body
        self.params = params or {}

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self): 
        self.handle_request('GET')

    def do_POST(self): 
        self.handle_request('POST')

    def handle_request(self, method):
        parsed = urlparse(self.path) # Tách path và query (sau dấu ?)
        
        path = parsed.path
        query = parse_qs(parsed.query) # "sort=asc&page=2" → {"sort": ["asc"], "page": ["2"]}
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode() if length else ''
        
        # Tìm xem URL + method này match với route nào
        for route_method, regex, handler in ROUTES:
            if route_method == method:
                match = regex.match(path) # Áp regex vào path để kiểm tra xem có khớp không
                if match:
                    params = match.groupdict()
                    request = Request(
                        method  = method,
                        path    = path,
                        query   = query,
                        headers = self.headers,
                        body    = body,
                        params  = params
                    )
                    # --- Middleware: attach current user vào request ---
                    raw = request.headers.get('Cookie', '')
                    cookies = parse_cookies(raw)
                    sid = cookies.get('session_id')
                    request.user = None
                    if sid:
                        sess = get_session(sid)
                        if sess:
                            request.user = User.find_by_id(sess['user_id'])
                    # ------------------------------------------------------
                    # Trả về response cho CLIENT
                    status, headers, response = handler(request)
                    
                    code, msg = status.split(' ', 1)
                    self.send_response(int(code), msg)
                    
                    for key, value in headers:
                        self.send_header(key, value)
                    self.end_headers()
                    
                    # Viết body ra socket (nếu có)
                    if response is not None:
                        # Nếu response là chuỗi, phải encode về bytes
                        ctype = dict(headers).get('Content-Type', '')
                        if isinstance(response, (bytes, bytearray)):
                            # Với dữ liệu nhị phân (ví dụ html binary), ghi trực tiếp
                            self.wfile.write(response)
                        elif ctype.startswith('image/'):
                            # Ảnh: đã decode Latin-1, bây giờ encode lại Latin-1
                            self.wfile.write(response.encode('latin-1'))
                        else:
                            # Text (HTML, CSS, JS…): encode UTF-8
                            self.wfile.write(response.encode('utf-8'))
                    return

        self.send_error(404, 'Page not found')

def run():
    server = HTTPServer(('', PORT), RequestHandler)
    print(f"Serving on http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
    finally:
        server.server_close()

if __name__ == '__main__':
    run()