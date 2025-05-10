from database import get_conn

PAYMENTS_TABLE = """
IF NOT EXISTS (
    SELECT * FROM sys.objects
    WHERE object_id = OBJECT_ID(N'dbo.payments')
    AND type IN (N'U')
) 
-- payments table
BEGIN
    CREATE TABLE dbo.Payments (
        PaymentID        INT            IDENTITY(1,1) PRIMARY KEY,
        OrderID          INT            NOT NULL,
        GatewaySessionID NVARCHAR(255)  NOT NULL,
        Status           NVARCHAR(50)   NOT NULL,
        Amount           DECIMAL(18, 2) NOT NULL,
        CreatedAt        DATETIME2      NOT NULL DEFAULT GETDATE(),
        UpdatedAt        DATETIME2      NULL,
        CONSTRAINT FK_Payments_Orders FOREIGN KEY (OrderID) REFERENCES dbo.Orders(Id)
    );
END
"""

def create_payments_table():
    """
    Tạo bảng Payments nếu chưa tồn tại.
    """
    conn = get_conn()
    cursor = conn.cursor()
    print("Tạo bảng Payments...")
    cursor.execute(PAYMENTS_TABLE)
    conn.close()
    print("Bảng Payments đã được tạo thành công.")