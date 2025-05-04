from database import get_conn

INIT_PASSWORD_RESET_TOKENS_SCHEMA = """
IF NOT EXISTS (
    SELECT * FROM sys.objects
    WHERE object_id = OBJECT_ID(N'[dbo].[PasswordResetTokens]') AND type = N'U'
)
CREATE TABLE dbo.PasswordResetTokens (
    Token NVARCHAR(64) PRIMARY KEY,
    UserID INT NOT NULL REFERENCES dbo.Users(UserID) ON DELETE CASCADE,
    ExpiresAt DATETIMEOFFSET NOT NULL
);
"""

def init_password_reset_tokens_schema():
    conn = get_conn()
    cur = conn.cursor()
    print("Tạo bảng PasswordResetTokens nếu chưa tồn tại...")
    cur.execute(INIT_PASSWORD_RESET_TOKENS_SCHEMA)
    conn.close()
    print("✅ Schema PasswordResetTokens đã tồn tại hoặc vừa được tạo.")