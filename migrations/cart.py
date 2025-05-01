from database import get_conn

# Tạo bảng Cart lưu tạm giỏ hàng của mỗi user (UserId, ProductId, Quantity)
SCHEMA_SQL = """
    IF NOT EXISTS (
        SELECT * FROM sys.objects
        WHERE object_id = OBJECT_ID(N'[dbo].[Cart]') AND type = N'U'
    )
    CREATE TABLE dbo.Cart (
        UserId     INT NOT NULL,
        ProductId  INT NOT NULL,
        Quantity   INT NOT NULL DEFAULT 1,
        CONSTRAINT PK_Cart          PRIMARY KEY (UserId , ProductId),
        CONSTRAINT FK_Cart_Users    FOREIGN KEY (UserId)    REFERENCES dbo.Users(UserID)    ON DELETE CASCADE,
        CONSTRAINT FK_Cart_Products FOREIGN KEY (ProductId) REFERENCES dbo.Products(ProductID) ON DELETE CASCADE
    );
"""
def init_cart_schema():
    """
    Khởi tạo schema cho bảng Cart nếu chưa tồn tại
    """
    conn = get_conn()
    cursor = conn.cursor()
    print("Tạo bảng Cart nếu chưa tồn tại...")
    cursor.execute(SCHEMA_SQL)
    conn.close()
    print("✅ Bảng Cart đã sẵn sàng.")