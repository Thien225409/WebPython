from database import get_conn

# Các lệnh tạo bảng Orders và OrderItems nếu chưa tồn tại
ORDERS_SQL = """
    IF NOT EXISTS (
        SELECT * FROM sys.objects
        WHERE object_id = OBJECT_ID(N'[dbo].[Orders]') AND type = N'U'
    )
    CREATE TABLE dbo.Orders (
      Id        INT           IDENTITY(1,1) PRIMARY KEY,
      UserId    INT           NOT NULL,
      Total     DECIMAL(18,2) NOT NULL,
      CreatedAt DATETIME2     NOT NULL DEFAULT GETDATE()  
    );
"""
ORDER_ITEMS_SQL = """
    IF NOT EXISTS (
        SELECT * FROM sys.objects
        WHERE object_id = OBJECT_ID(N'[dbo].[OrderItems]') AND type = N'U'
    )
    CREATE TABLE dbo.OrderItems (
        Id         INT           IDENTITY(1,1) PRIMARY KEY,
        OrderId    INT           NOT NULL,
        ProductId  INT           NOT NULL,
        Quantity   INT           NOT NULL,
        UnitPrice  DECIMAL(18,2) NOT NULL,
        CONSTRAINT FK_OrderItems_Orders   FOREIGN KEY (OrderId)   REFERENCES dbo.Orders(Id)   ON DELETE CASCADE,
        CONSTRAINT FK_OrderItems_Products FOREIGN KEY (ProductId) REFERENCES dbo.Products(ProductID)
    );
"""
def init_order_schema():
    """
    Tạo bảng Orders và OrderItems nếu chưa tồn tại.
    """
    conn = get_conn()
    cursor = conn.cursor()
    print("Tạo bảng Orders và OrderItems...")
    cursor.execute(ORDERS_SQL)
    cursor.execute(ORDER_ITEMS_SQL)
    conn.close()
    print("✅ Schema Orders/OrderItems đã tồn tại hoặc vừa được tạo.")