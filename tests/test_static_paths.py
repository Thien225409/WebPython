import pytest
from pathlib import Path

# Thư mục chứa các file template của dự án
TEMPLATES_DIR = Path(__file__).parent.parent / 'templates'

@pytest.mark.parametrize('tpl_path', sorted(TEMPLATES_DIR.glob('*.html')))
def test_no_static_image_references(tpl_path):
    """
    Đảm bảo không có reference tới /static/images/ trong các template.
    """
    content = tpl_path.read_text(encoding='utf-8')
    assert '/static/images/' not in content, (
        f'Template {tpl_path.name} vẫn tham chiếu /static/images/, cần chuyển sang /public/images/'
    )

@pytest.mark.parametrize('tpl_name', ['base.html', 'index.html', 'product_detail.html'])
def test_public_image_references_exist(tpl_name):
    """
    Kiểm tra các template chính:
    - Với base.html: phải có reference tới /public/images/
    - Với index.html và product_detail.html: phải sử dụng biến image_url để load ảnh động
    """
    tpl_path = TEMPLATES_DIR / tpl_name
    assert tpl_path.exists(), f'Không tìm thấy template {tpl_name}'
    content = tpl_path.read_text(encoding='utf-8')
    if tpl_name == 'base.html':
        assert '/public/images/' in content, (
            f'Template {tpl_name} chưa tham chiếu /public/images/, cần thêm đúng đường dẫn hình ảnh'
        )
    else:
        # index.html, product_detail.html
        assert 'image_url' in content, (
            f'Template {tpl_name} phải sử dụng biến image_url để load ảnh, kiểm tra src="{{ p.image_url }}" hoặc src="{{ product.image_url }}"'
        )
