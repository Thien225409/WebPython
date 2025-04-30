# routes/static_routes.py
import os,mimetypes
from routes.router import add_route

def static_handler(request):
    fp = os.path.join(os.getcwd(), request.path.lstrip('/'))
    if not os.path.isfile(fp):
        return '404 Not Found', [('Content-Type','text/plain')], 'Not found'
    ctype, _ = mimetypes.guess_type(fp)
    data = open(fp, 'rb').read()
    return '200 OK', [('Content-Type', ctype or 'application/octet-stream')], data.decode('latin-1')

add_route('GET', r'^/public/.*$', static_handler)