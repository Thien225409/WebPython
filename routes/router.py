# routes/router.py
import re

# Global registry
ROUTES = []

def add_route(method, path_pattern, handler):
    """
    Đăng ký route:
      - method: 'GET'/'POST'/...
      - path_pattern: regex pattern (string)
      - handler: function(request) -> (status, headers, body)
    """
    ROUTES.append((method.upper(), re.compile(path_pattern), handler))
