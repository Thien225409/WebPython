# migrations/init_db.py
from migrations.products import init_prod_schema,    seed_prod
from migrations.users    import init_user_schema,    seed_user
from migrations.sessions import init_session_schema, seed_session 
from migrations.add_fk_sessions_users import init_fk_sessions_users_schema
from migrations.cart     import init_cart_schema
from migrations.order    import init_order_schema
from migrations.add_email_to_users import migrate_add_email
from migrations.password_reset_token import init_password_reset_tokens_schema
def main():
    # Products
    print("=== Khởi tạo Products ===")
    init_prod_schema()
    seed_prod()
    print("Hoàn tất khởi tạo Products")
    
    # Users
    print("\n=== Khởi tạo Users ===")
    init_user_schema()
    seed_user()
    print("Hoàn tất khởi tạo Users")
    
    # chạy migration thêm Email
    migrate_add_email()
    
    # PasswordResetTokens
    print("\n=== Khởi tạo PasswordResetTokens ===")
    init_password_reset_tokens_schema()
    print("Hoàn tất khởi tạo PasswordResetTokens")
    
    # Sessions
    print("\n=== Khởi tạo Sessions ===")
    init_session_schema()
    seed_session()
    print("Hoàn tất khởi tạo Sessions")
    
    # FK Sessions Users
    print("\n=== Khởi tạo FK Sessions Users ===")
    init_fk_sessions_users_schema()
    print("Hoàn tất khởi tạo FK Sessions Users")
    
    # Cart
    print("\n=== Khởi tạo Cart ===")
    init_cart_schema()
    print("Hoàn tất khởi tạo giỏ hàng")
    
    # Orders/OrderItems
    print("\n=== Khởi tạo Orders/OrderItems ===")
    init_order_schema()
    print("Hoàn tất khởi tạo đơn hàng")
if __name__ == '__main__':
    main()