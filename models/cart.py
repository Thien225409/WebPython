from database import get_conn

class Cart:
    @staticmethod
    def add_item(user_id: int, product_id: int, quantity: int =1) -> None:
        conn = get_conn()
        cursor = conn.cursor()
        # Kiểm tra nếu đã có mục này trong Cart
        cursor.execute (
            "SELECT Quantity FROM Cart WHERE UserId=? AND ProductId=?",
            (user_id, product_id)
        )
        row = cursor.fetchone()
        if row:
            # Nếu đã có sản phẩm này trong giỏ của người dùng thì tăng số lượng thêm 1.
            new_qty = row.Quantity + quantity
            cursor.execute (
                "UPDATE Cart SET Quantity=? WHERE UserId=? AND ProductId=?",
                (new_qty, user_id, product_id)
            )
        else:
            # Nếu chưa có sản phẩm này thì thêm vào db
            cursor.execute (
                "INSERT INTO Cart (UserId, ProductId, Quantity) VALUES (?,?,?)",
                (user_id, product_id, quantity)
            )
        conn.close()
    
    @staticmethod
    def remove_item(user_id: int, product_id: int) -> None:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Cart WHERE UserId=? AND ProductId=?",
            (user_id, product_id)
        )
        conn.close()
    
    @staticmethod
    def get_items(user_id: int) -> dict[int, int]:
        """
        Lấy ra những sản phẩm của người có id = user_id
        Trả về tất cả các sản phẩm đó theo dạng ProductId:Quantity của người đó
        """
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ProductId, Quantity FROM Cart WHERE UserId=?",
            user_id
        )
        rows = cursor.fetchall()
        conn.close()
        return {row.ProductId: row.Quantity for row in rows}
    
    @staticmethod
    def clear(user_id: int) -> None:
        """
        Xóa giỏ hàng của người có id = user_id
        """
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Cart WHERE UserId=?",
            user_id
        )
        conn.close()
        
            