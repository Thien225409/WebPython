from datetime import datetime
from typing import Optional
import pyodbc
from database import get_conn
from utils.security import hash_password, verify_password

class User:
    """
    ORM lớp User với các phương thức CRUD cơ bản,
    đăng ký và xác thực mật khẩu hashed.
    """
    def __init__(self, user_id: int, username: str, password_hash: str, created_at: datetime, is_admin: bool = False):
        self.user_id        = user_id
        self.username       = username
        self._password_hash = password_hash
        self.created_at     = created_at
        self.is_admin       = is_admin 
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """
        Trả về User instance nếu tìm thấy theo username, ngược lại None.
        """
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT UserID, Username, PasswordHash, CreatedAt, IsAdmin "
            "FROM dbo.Users WHERE Username = ?;",
            (username,)
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return cls(
            user_id       = row.UserID,
            username      = row.Username,
            password_hash = row.PasswordHash,
            created_at    = row.CreatedAt,
            is_admin      = bool(row.IsAdmin)
        )
    @classmethod
    def find_by_id(cls, user_id: int) -> Optional['User']:
        """
        Trả về User instance nếu tìm thấy theo UserID, ngược lại None.
        """
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT UserID, Username, PasswordHash, CreatedAt, IsAdmin"
            " FROM dbo.Users WHERE UserID = ?;",
            (user_id,)
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return cls(
            user_id       = row.UserID,
            username      = row.Username,
            password_hash = row.PasswordHash,
            created_at    = row.CreatedAt,
            is_admin      = bool(row.IsAdmin)
        )
    @classmethod
    def register(cls, username: str, password: str) -> 'User':
        """
        Đăng ký user mới:
        - Hash mật khẩu
        - Lưu vào database
        - Trả về instance User vừa tạo
        """
        pwd_hash = hash_password(password)
        conn = get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO dbo.Users (Username, PasswordHash) VALUES (?, ?);",
                (username, pwd_hash)
            )
        except pyodbc.IntegrityError:
            conn.rollback()
            raise ValueError(f"Username '{username}' đã tồn tại.")
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        return cls.find_by_username(username)
    def check_password(self, password: str) -> bool:
        """
        Xác thực mật khẩu nhập vào so với hash đã lưu.
        """
        return verify_password(self._password_hash, password)
    def __repr__(self) -> str:
        return f"<User id={self.user_id} username={self.username}>"
#     import os
# import hashlib
# import hmac
# import binascii

# """
# Module cung cấp hàm hash và verify mật khẩu dùng PBKDF2-HMAC-SHA256.
# """

# def hash_password(password: str) -> str:
#     """
#     Sinh salt ngẫu nhiên và hash password với PBKDF2-HMAC-SHA256.
#     Kết quả là hex(salt + hash).
#     """
#     salt = os.urandom(16)
#     pwdhash = hashlib.pbkdf2_hmac(
#         'sha256',
#         password.encode('utf-8'),
#         salt,
#         100_000
#     )
#     return binascii.hexlify(salt + pwdhash).decode('ascii')

# def verify_password(stored_hash: str, password: str) -> bool:
#     """
#     Kiểm tra password nhập vào so với stored_hash (hex của salt+hash).
#     """
#     data = binascii.unhexlify(stored_hash.encode('ascii'))
#     salt = data[:16]
#     original_hash = data[16:]
#     new_hash = hashlib.pbkdf2_hmac (
#         'sha256',
#         password.encode('utf-8'),
#         salt,
#         100_000
#     ) 
#     return hmac.compare_digest(original_hash, new_hash)
    