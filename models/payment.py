from database import get_conn

class Payment:
    """
    ORM cho bảng Payments.
    """
    @staticmethod
    def create(order_id: int, gateway_session_id: str, amount: float, status: str) -> None:
        """
        Ghi một bản ghi mới vào bảng dbo.Payments.
        - order_id:    khóa đơn hàng (Orders.Id)
        - gateway_session_id: mã định danh giao dịch (như 'QR_<order_id>')
        - amount:      số tiền thanh toán
        - status:      'paid' | 'pending' | 'failed'
        """
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Payments (OrderID, GatewaySessionID, Amount, Status)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, gateway_session_id, amount, status)
        )
        conn.close()
    
    @staticmethod
    def uptate_status(payment_id: int, status: str) -> None:
        """
        Cập nhật trạng thái thanh toán.
        """
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Payments
            SET Status = ?
            WHERE PaymentID = ?
            """,
            (status, payment_id)
        )
        conn.close()
    
    @staticmethod
    def find_by_order(order_id: int):
        """
        Lấy Payment theo order_id (nếu cần).
        Trả về dict hoặc None.
        """
        conn   = get_conn()
        cursor = conn.cursor()
        row = cursor.execute(
            """
            SELECT PaymentID, GatewaySessionID, Amount, Status, CreatedAt, UpdatedAt
            FROM dbo.Payments
            WHERE OrderID = ?;
            """,
            (order_id,)
        ).fetchone()
        conn.close()
        if not row:
            return None
        return {
            'payment_id':       row.PaymentID,
            'gateway_session':  row.GatewaySessionID,
            'amount':           float(row.Amount),
            'status':           row.Status,
            'created_at':       row.CreatedAt,
            'updated_at':       row.UpdatedAt,
        }