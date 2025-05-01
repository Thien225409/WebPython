# migrations/products.py
from database import get_conn
# Sử dụng hàm get_conn hợp pháp trong file này

# Định nghĩa lệnh tạo bảng (SCHEMA)
# """""" : chuỗi nhiều dòng
# SCHEMA_SQL: là một list các câu lệnh T-SQL-> tạo bảng
SCHEMA_SQL = """
    IF NOT EXISTS (
        SELECT * FROM sys.objects
        WHERE object_id = OBJECT_ID(N'[dbo].[Products]')
                            AND type in(N'U')
    )
    CREATE TABLE [dbo].[Products] (
        ProductID    INT           IDENTITY(1,1) PRIMARY KEY,
        Name         NVARCHAR(100) NOT NULL,
        Price        DECIMAL(18,2) NOT NULL,
        Stock        INT           NOT NULL,
        Decription   NVARCHAR(500) NULL,
        ImageURL     NVARCHAR(200) NULL
    );
"""

# Các câu lệnh INSERT mẫu, chỉ chạy khi bảng còn trống
SEED_SQL = """
    INSERT INTO [dbo].[Products] (Name, Price, Stock, Decription, ImageURL)
    VALUES
        (N'Ba chỉ thượng hạng', 160000, 30, N'Thịt ba chỉ thượng hạng, lớp mỡ và nạc xen kẽ hoàn hảo, rất thích hợp để nướng hoặc kho tàu.', N'/public/images/suon_thuong_hang.png'),
        (N'Nạc vai ngon',       150000, 20, N'Nạc vai mềm, ít mỡ, phù hợp để xào, làm nem hoặc nướng.', N'/public/images/thit_vai.png'),
        (N'Sườn thăn',          120000, 30, N'Sườn thăn nhiều thịt, Sườn hồng tươi với thịt mềm căng mọng được tuyển chọn kỹ lưỡng từ tảng sườn thăn ngon nhất. Là nguyên liệu hảo hạng cho món ngon đúng điệu.', N'/public/images/suon_than.png'),
        (N'Bắp giò cuộn',       120000, 30, N'Thịt chân giò được pha lóc bỏ xương, cuộn tròn tỉ mỉ, là sự tổng hòa hương vị của thịt mềm ngọt, da béo thơm.', N'/public/images/chan_gio_cuon.png'),
        (N'Ba rọi rút xương',   120000, 20, N'Được lựa chọn từ phần thịt ba rọi ngon nhất với vị thơm ngon, béo ngậy đặc trưng, ba rọi rút sườn là sự kết hợp hài hòa giữa lớp thịt ba rọi mềm căng mọng và sụn giòn sần sật.', N'/public/images/mong_gio.png'),
        (N'Nạc đậm, đầu giòn',  120000, 30, N'Kết hợp giữa nạc đậm và đầu heo giòn sựt, rất ngon khi làm món xào hoặc nướng.', N'/public/images/nac_dam_dau_gion.png'),
        (N'Nạc nóng',           150000, 28, N'Thịt nạc nóng vừa giết mổ, tươi nguyên, thích hợp cho các món xào, nướng, kho.', N'/public/images/nac_nong.png'),
        (N'Thịt xay',           57000,  25, N'Thịt heo xay ủ mát chuẩn Âu giúp thịt mềm, mọng, giữ nguyên dinh dưỡng. Phù hợp làm thịt viên, nhồi khổ qua, hoặc xào mướp.', N'/public/images/thit_xay.png'),
        (N'Thăn heo',           135000, 22, N'Thăn heo là phần nạc mềm nhất, rất ít mỡ, lý tưởng để chiên xù hoặc nướng.', N'/public/images/than.png')
    ;
"""


# Ham khoi tao DB
def init_prod_schema():
    conn = get_conn()
    cursor = conn.cursor() # Biến con trỏ tới kết nối đó
    
    # 1. Tao schema (cac bang)
    print("Chạy lệnh tạo bảng...")
    cursor.execute(SCHEMA_SQL)
    print("Schema đã áp dụng xong.")
    conn.close()
def seed_prod():
    conn = get_conn()
    cursor = conn.cursor()
    # 2. Kiem tra bang Products co bao nhieu ban ghi
    cursor.execute("SELECT COUNT(*) FROM [dbo].[Products]")
    count = cursor.fetchone()[0] # Lay ban ghi dau tien tu ket qua tren (co mot ban ghi thoi)
    if count == 0:
        print("Bảng Products trống, sẽ seed dữ liệu mẫu...")
        cursor.execute(SEED_SQL)
        print("Đã seed dữ liệu mẫu.")
    else:
        print(f"Đã có {count} bản ghi, bỏ qua lệnh seed.")
    conn.close() # Dong ket noi
