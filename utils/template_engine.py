from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

# setup Jinja env
env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),'..','templates')),
    autoescape=select_autoescape(['html','xml'])
)

def render_template(name, context=None, request=None):
    """
    name: tên file .html
    context: dict biến riêng cho page
    request: chuyển vào template để check request.user, request.path…
    """
    ctx = context.copy() if context else {}
    if request:
        # Make request available as a global in all templates
        env.globals['request'] = request
    return env.get_template(name).render(**ctx)
