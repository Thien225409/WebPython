# migrations/users.py
from database import get_conn

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
    )
"""

USER_SEED = """
    IF NOT EXISTS (SELECT * FORM dbo.Users
                   WHERE Username = N'admin')
    BEGIN
        -- Thay <HASH> bằng giá trị hash thực tế của password mặc định
        INSERT INTO dbo.Users (Username, PasswordHash)
        VALUES (N'admin', N'<HASH>');
    END
"""

def init_schema ():
    conn = get_conn()
    cursor = conn.cursor()
    print("Tạo bảng Users...")
    cursor.execute(USER_SCHEMA)
    conn.close()

def seed_data():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM dbo.Users")
    if cursor.fetchone()[0] == 0:
        print("Seed dữ liệu Users…")
        cursor.execute(USER_SEED)
    else:
        print("Users đã có dữ liệu, bỏ qua seed.")
    conn.close()
    