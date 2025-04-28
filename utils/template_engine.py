from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

# Thiết lập môi trường Jinja2, loader trỏ đến thư mục templates
env = Environment(
    # loader tìm đến thư mục templates
    loader = FileSystemLoader(
        os.path.join(os.path.dirname(__file__), '..', 'templates')
    ),
    autoescape = select_autoescape(['html', 'xml'])
)

def render_template(name, context):
    """
    name: tên file .html trong folder templates
    context: dict chứa các biến để truyền vào template
    """
    tmpl = env.get_template(name)
    return tmpl.render(**context)
