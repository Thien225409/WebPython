# conftest.py
from types import SimpleNamespace

def fake_request(method='GET', path='/', body='', headers=None, cookies=None, user=None, params=None):
    headers = headers or {}
    cookies = cookies or {}
    cookie_str = '; '.join(f'{k}={v}' for k, v in cookies.items())
    headers['Cookie'] = cookie_str

    return SimpleNamespace(
        method=method,
        path=path,
        query={},
        headers=headers,
        body=body,
        params=params or {},
        user=user
    )
