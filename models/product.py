# models/product.py
from database import get_conn
# Mỗi khi cần truy vấn sẽ gọi get_conn()

class Product:
    """
    Class địa diện cho bảng Products
    Mỗi instance tương ứng một bản ghi trong bảng
    """
    
    # __init__: Khởi tạo object với các thuộc tính tưogn ứng cột trong bảng
    # Sử dụng pythonic cho thuộc tính -> map thẳng sang các cột SQL
    def __init__(self, product_id, name, price, stock, decription, image_url):
        self.product_id  = product_id
        self.name        = name
        self.price       = price
        self.stock       = stock
        self.decription = decription
        self.image_url   = image_url
    # end __init__
    
    @staticmethod
    def all():
        """
        Trả về danh sách tất cả sản phẩm dưới dạng list các đối tượng Product
        """
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT ProductID, Name, Price, Stock, Decription, ImageURL "
                       "FROM dbo.Products")
        rows = cursor.fetchall()
        conn.close()
        
        products = []
        for row in rows:
            # row.ProductID...
            prod = Product(
                product_id  = row.ProductID,
                name        = row.Name,
                price       = float(row.Price),
                stock       = row.Stock,
                decription = row.Decription,
                image_url   = row.ImageURL
            )
            products.append(prod)
        return products
    # end all()
    
    @staticmethod
    def find_by_id(product_id):
        """
        Trả về đối tượng Product có ProductID = product_id, hoặc None nếu không tìm thấy.
        """
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ProductID, Name, Price, Stock, Decription, ImageURL "
            "FROM dbo.Products WHERE ProductID = ?",product_id
        )
        row = cursor.fetchone()
        conn.close()
        if row:# Neu row da co thi lay ra thong tin
            return Product(
                product_id = row.ProductID,
                name       = row.Name,
                price      = float(row.Price),
                stock      = row.Stock,
                decription = row.Decription,
                image_url  = row.ImageURL
            )
        return None
    # end find_by_id
    
    @staticmethod
    def create(name, price, stock, decription=None, image_url=None):
        """
        Chèn một sản phẩm mới vào bảng, và trả về object Product vừa tạo (có ID).
        """
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """
                INSERT INTO dbo.Products (Name, Price, Stock, Decription, ImageURL)
                OUTPUT INSERTED.ProductID
                VALUES (?, ?, ?, ?, ?);
            """,
            (name, price, stock, decription, image_url)
        )
        # OUTPUT INSERTED.<PK> sẽ trả về một recordset, fetchone()[0] là ID mới
        row = cursor.fetchone()
        new_id = int(row[0])
        print(f"[DEBUG] Created product ID: {new_id}")  # ✅ In ra ID được tạo
        product = Product.find_by_id(new_id)
        print(f"[DEBUG] Product created object: {product}")  # ✅ In ra object trả về
        return product
    # end create
    
    def update(self):
        """
        Cập nhật bản ghi trong DB theo giá trị hiện tại của thuộc tính instance.
        """
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE dbo.Products SET Name = ?, Price = ?, Stock = ?, Decription = ?, ImageURL = ? "
            "WHERE ProductID = ?;",
            self.name, self.price, self.stock, self.decription, self.image_url, self.product_id
        )
        print(f"Đã cập nhật bản ghi có ProductID = {self.product_id}.")
        conn.close()
    # end update
    
    def delete(self):
        """
        Xóa bản ghi tương ứng với instance khỏi DB.
        """
        conn = get_conn()
        cursor = conn.cursor()
        # Kiểm tra xem bản ghi có tồn tại không
        cursor.execute(
            "SELECT COUNT(*) FROM dbo.Products WHERE ProductID = ?;", 
            self.product_id
        )
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"Không tìm thấy bản ghi có ProductID = {self.product_id}.")
        else:
            # Neu cos thi xoa no di
            cursor.execute(
                "DELETE FROM dbo.Products WHERE ProductID = ?;",
                self.product_id
            )
            print(f"Đã xóa bản ghi có ProductID = {self.product_id}.")
        conn.close()
    # end delete()
# end class Product