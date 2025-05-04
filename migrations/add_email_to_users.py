# migrations/add_email_to_users.py
"""
Migration: thêm cột Email vào dbo.Users (nếu chưa có)
"""
from database import get_conn
from config import ADMIN_EMAIL, ADMIN

ADD_COLUM_EMAIL = """
    IF NOT EXISTS (
      SELECT * FROM sys.objects
      WHERE object_id = OBJECT_ID(N'[dbo].[Users]')
        AND type = N'U'
    )
      PRINT 'Bảng Users chưa tồn tại, bỏ qua migration add_email.'
    ELSE
      BEGIN
        -- 2) Nếu cột Email chưa tồn tại thì thêm vào
        IF NOT EXISTS (
          SELECT * FROM sys.columns
          WHERE Name = N'Email'
            AND Object_ID = OBJECT_ID(N'[dbo].[Users]')
        )
        BEGIN
          ALTER TABLE dbo.Users
            ADD Email NVARCHAR(100) NOT NULL DEFAULT '';
          PRINT 'Đã thêm cột Email vào dbo.Users.';
        END
        ELSE
          PRINT 'Cột Email đã tồn tại, bỏ qua.';
      END

"""
def migrate_add_email():
    conn = get_conn()
    cur = conn.cursor()

    print("Kiểm tra và thêm cột Email vào dbo.Users nếu cần...")

    # 1) Nếu bảng Users chưa tồn tại, bỏ qua
    cur.execute(ADD_COLUM_EMAIL)
    # Cập nhật email cho admin
    print("Cập nhật email cho admin nếu cần...")
    cur.execute(
        """
        UPDATE dbo.Users
        SET Email = ?
        WHERE Username = ?;
        """, (ADMIN_EMAIL, ADMIN)
    )
    conn.close()
    print("✅ Migration add_email_to_users hoàn tất.")
