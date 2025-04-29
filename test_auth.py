# test_auth.py

import http.client
import urllib.parse

HOST = 'localhost'
PORT = 8000

def test_register(username, password):
    conn = http.client.HTTPConnection(HOST, PORT)
    params = urllib.parse.urlencode({'username': username, 'password': password})
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/register', params, headers)
    res = conn.getresponse()
    print(f'[REGISTER] {username=} {res.status=} {res.reason}')
    # Nếu redirect về /login thì đúng
    if res.status == 303:
        print('  ✔ Redirect to', res.getheader('Location'))
    else:
        print('  ✘', res.read().decode())
    conn.close()

def test_login(username, password):
    conn = http.client.HTTPConnection(HOST, PORT)
    params = urllib.parse.urlencode({'username': username, 'password': password})
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/login', params, headers)
    res = conn.getresponse()
    print(f'[LOGIN]  {username=} {res.status=} {res.reason}')
    cookie = res.getheader('Set-Cookie')
    if res.status == 303 and cookie and 'session_id=' in cookie:
        print('  ✔ Got session cookie:', cookie.split(';')[0])
    else:
        print('  ✘', res.read().decode())
    conn.close()
    return cookie

def test_wrong_login(username, password):
    conn = http.client.HTTPConnection(HOST, PORT)
    params = urllib.parse.urlencode({'username': username, 'password': password})
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/login', params, headers)
    res = conn.getresponse()
    print(f'[WRONG LOGIN] {username=} {res.status=} {res.reason}')
    body = res.read().decode()
    print('  ✔ Response body:', body.strip())
    conn.close()

def test_logout(cookie):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {'Cookie': cookie}
    conn.request('GET', '/logout', headers=headers)
    res = conn.getresponse()
    print(f'[LOGOUT] {res.status=} {res.reason}')
    del_cookie = res.getheader('Set-Cookie')
    print('  ✔ Deleted cookie header:', del_cookie)
    conn.close()

if __name__ == '__main__':
    username = 'testuser'
    password = 'TestPass123'
    print('--- Testing Register ---')
    test_register(username, password)
    print('\n--- Testing Login ---')
    cookie = test_login(username, password)
    print('\n--- Testing Wrong Login ---')
    test_wrong_login(username, 'wrongpassword')
    print('\n--- Testing Logout ---')
    test_logout(cookie)
