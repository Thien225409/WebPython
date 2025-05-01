# migrations/sessions.py
from config import SESSION_TTL_HOURS
from database import get_conn

# Tạo bảng Sessions nếu chưa tồn tại
SESSIONS_SCHEMA = """
IF NOT EXISTS (
    SELECT * FROM sys.objects
    WHERE object_id = OBJECT_ID(N'[dbo].[Sessions]') AND type = N'U'
)
CREATE TABLE dbo.Sessions (
    SessionId    UNIQUEIDENTIFIER PRIMARY KEY,
    UserId       INT               NOT NULL,
    CreatedAt    DATETIMEOFFSET    NOT NULL DEFAULT SYSDATETIMEOFFSET(),
    ExpiresAt    DATETIMEOFFSET    NOT NULL
);
-- Tạo index để dễ xoá session cũ
IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = N'IX_Sessions_ExpiresAt' AND object_id = OBJECT_ID(N'[dbo].[Sessions]')
)
CREATE INDEX IX_Sessions_ExpiresAt ON dbo.Sessions(ExpiresAt);
"""

def init_session_schema():
    """
    Tạo bảng Sessions nếu chưa tồn tại.
    """
    conn = get_conn()
    cur = conn.cursor()
    print("Tạo bảng Sessions...")
    cur.execute(SESSIONS_SCHEMA)
    conn.close()
    print("✅ Schema Sessions đã tồn tại hoặc vừa được tạo.")

def seed_session():
    """
    (Không cần seed dữ liệu cho bảng Sessions, vì session tạo động khi user login.)
    Nhưng ở đây ta có thể xoá sạch các session đã hết hạn ngay khi khởi migrations.
    """
    conn = get_conn()
    cur = conn.cursor()
    # Xoá các session đã hết hạn
    print("Xoá các session đã hết hạn...")
    cur.execute(
        "DELETE FROM dbo.Sessions WHERE ExpiresAt < SYSDATETIMEOFFSET();"
    )
    deleted = cur.rowcount
    conn.close()
    print(f"🎉 Đã xoá {deleted} session cũ.")
