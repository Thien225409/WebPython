import os
import hashlib
import hmac
import binascii

"""
Module cung cấp hàm hash và verify mật khẩu dùng PBKDF2-HMAC-SHA256.
"""

def hash_password(password: str) -> str:
    """
    Sinh salt ngẫu nhiên và hash password với PBKDF2-HMAC-SHA256.
    Kết quả là hex(salt + hash).
    """
    salt = os.urandom(16)
    pwdhash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100_000
    )
    return binascii.hexlify(salt + pwdhash).decode('ascii')

def verify_password(stored_hash: str, password: str) -> bool:
    """
    Kiểm tra password nhập vào so với stored_hash (hex của salt+hash).
    """
    data = binascii.unhexlify(stored_hash.encode('ascii'))
    salt = data[:16]
    original_hash = data[16:]
    new_hash = hashlib.pbkdf2_hmac (
        'sha256',
        password.encode('utf-8'),
        salt,
        100_000
    ) 
    return hmac.compare_digest(original_hash, new_hash)