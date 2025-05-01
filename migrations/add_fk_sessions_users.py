from database import get_conn

SCHEMA_SQL = """
    IF NOT EXISTS (
        SELECT 1 FROM sys.foreign_keys
        WHERE name = 'FK_Sessions_Users'
    )
    BEGIN
        ALTER TABLE dbo.Sessions
        ADD CONSTRAINT FK_Sessions_Users
            FOREIGN KEY (UserId)
            REFERENCES dbo.Users(UserID)
            ON DELETE CASCADE;
    END
"""

def init_fk_sessions_users_schema():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(SCHEMA_SQL)
    conn.close()
    print("✅ Đã thêm khóa ngoại FK_Sessions_Users giữa Sessions.UserId và Users.UserID.")