# migrations/init_db.py
from migrations.products import init_schema as init_prod_schema, seed_data as seed_prod
from migrations.users    import init_schema as init_user_schema, seed_data as seed_user
from migrations.sessions import init_schema as init_session_schema, seed_data as seed_session 
def main():
    # Products
    print("=== Khởi tạo Products ===")
    init_prod_schema()
    seed_prod()
    
    # Users
    print("\n=== Khởi tạo Users ===")
    init_user_schema()
    seed_user()
    print("Hoàn tất khởi tạo database")
    
    # Sessions
    print("\n=== Khởi tạo Sessions ===")
    init_session_schema()
    seed_session()
    print("Hoàn tất khởi tạo database")
if __name__ == '__main__':
    main()