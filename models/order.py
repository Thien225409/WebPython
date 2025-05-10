from database import get_conn

class Order:
    @staticmethod
    def list_by_user(user_id: int) -> list[dict]:
        """
        Lấy danh sách đơn đã mua của user, mỗi phần tử là dict(Id, Total, CreatedAt).
        """
        conn  = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Id, Total, CreatedAt FROM dbo.Orders WHERE UserId = ? ORDER BY CreatedAt DESC",
            user_id
        )
        # Lấy ra tất cả các hàng chính là các đơn đã mua của user_id
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                'Id':        row.Id,
                'Total':     row.Total,
                'CreatedAt': row.CreatedAt
            }
            for row in rows
        ]
        
    @staticmethod
    def create(user_id: int, items: list[dict], total: float) -> int:
        """
        Tạo Order và OrderItems.
        items: [{'product': <Product>, 'qty': n}, ...]
        Trả về order_id (IDENTITY).
        """
        conn  = get_conn()
        cursor = conn.cursor()
        # Tạo Order
        cursor.execute (
            "INSERT INTO dbo.Orders (UserId, Total) OUTPUT INSERTED.Id VALUES (?, ?)",
            (user_id, total)
        )
        order_id = cursor.fetchone()[0]
        # Tạo từng OrderItem
        for it in items:
            product = it['product']
            quantity = it['qty'] # Số lượng mua
            cursor.execute (
                """
                INSERT INTO dbo.OrderItems
                    (OrderId, ProductId, Quantity, UnitPrice)
                VALUES (?,?,?,?)
                """,
                (order_id, product.product_id, quantity, product.price)
            )
        conn.close()
        return order_id
    @staticmethod
    def items(order_id: int) -> list[dict]:
        """
        Lấy chi tiết các sản phẩm trong một order.
        Trả về list [{'product_id':…, 'qty':…, 'unit_price':…}, …].
        """
        conn  = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT ProductId, Quantity, UnitPrice
            FROM dbo.OrderItems
            WHERE OrderId = ?
            """,
            order_id
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                'product_id': r.ProductId,
                'qty':        r.Quantity,
                'unit_price': r.UnitPrice
            }
            for r in rows
        ]
        
        
        