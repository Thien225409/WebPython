# migrations/products.py
from database import get_conn
# Sử dụng hàm get_conn hợp pháp trong file này

# Định nghĩa lệnh tạo bảng (SCHEMA)
# """""" : chuỗi nhiều dòng
# SCHEMA_SQL: là một list các câu lệnh T-SQL-> tạo bảng
SCHEMA_SQL = [
    """
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
]

# Các câu lệnh INSERT mẫu, chỉ chạy khi bảng còn trống
SEED_SQL = [
    """
    INSERT INTO [dbo].[Products] (Name, Price, Stock, Decription, ImageURL)
    VALUES
         (N'Ba chỉ thượng hạng', 160000, 30, N'Mỡ & nạc xen kẽ hoàn hảo', '/static/images/suon_thuong_hang.png'),
        (N'Nạc vai ngon',      150000, 20, N'Nạc vai mềm, ít mỡ, phù hợp xào', '/static/images/thit_vai.png')
    ;
    """
]

# Ham khoi tao DB
def init_schema():
    conn = get_conn()
    cursor = conn.cursor() # Biến con trỏ tới kết nối đó
    
    # 1. Tao schema (cac bang)
    for sql in SCHEMA_SQL:# Duyet tung lenh sql trong schema
        print("Chạy lệnh tạo bảng...")
        cursor.execute(sql) # Chay tung lenh do
    print("Schema đã áp dụng xong.")
    conn.close()
def seed_data():
    conn = get_conn()
    cursor = conn.cursor()
    # 2. Kiem tra bang Products co bao nhieu ban ghi
    cursor.execute("SELECT COUNT(*) FROM [dbo].[Products]")
    count = cursor.fetchone()[0] # Lay ban ghi dau tien tu ket qua tren (co mot ban ghi thoi)
    if count == 0:
        print("Bảng Products trống, sẽ seed dữ liệu mẫu...")
        for sql in SEED_SQL:
            cursor.execute(sql)
        print("Đã seed dữ liệu mẫu.")
    else:
        print(f"Đã có {count} bản ghi, bỏ qua lệnh seed.")
    conn.close() # Dong ket noi
