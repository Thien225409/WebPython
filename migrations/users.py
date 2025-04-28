# migrations/users.py
import os
import hashlib
import binascii
from config import ADMIN, ADMIN_PASSWORD
from database import get_conn


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

USER_SCHEMA = """
IF NOT EXISTS (
    SELECT * FROM sys.objects
    WHERE object_id = OBJECT_ID(N'[dbo].[Users]') AND type = N'U'
)
CREATE TABLE dbo.Users (
    UserID       INT           IDENTITY(1,1) PRIMARY KEY,
    Username     NVARCHAR(50)  NOT NULL UNIQUE,
    PasswordHash NVARCHAR(200) NOT NULL,
    CreatedAt    DATETIME      NOT NULL DEFAULT GETDATE()
);
"""


def init_schema():
    """
    Tạo bảng Users nếu chưa tồn tại.
    """
    conn = get_conn()
    cur = conn.cursor()
    print("Tạo bảng Users...")
    cur.execute(USER_SCHEMA)
    conn.close()
    print("✅ Schema Users đã tồn tại hoặc vừa được tạo.")


def seed_data():
    """
    Seed tài khoản admin nếu chưa có.
    ADMIN và ADMIN_PASSWORD lấy từ config.py.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Kiểm tra user admin đã tồn tại?
    cur.execute(
        "SELECT COUNT(*) FROM dbo.Users WHERE Username = ?;",
        (ADMIN,)
    )
    exists = cur.fetchone()[0] > 0

    if exists:
        print(f"User '{ADMIN}' đã tồn tại, bỏ qua seed.")
    else:
        print("Seed dữ liệu Users (tài khoản admin)...")
        pwd_hash = hash_password(ADMIN_PASSWORD)
        cur.execute(
            "INSERT INTO dbo.Users (Username, PasswordHash) VALUES (?, ?);",
            (ADMIN, pwd_hash)
        )
        print(f"✅ Đã thêm user '{ADMIN}' thành công.")

    conn.close()
    print("🎉 Hoàn tất seed Users.")