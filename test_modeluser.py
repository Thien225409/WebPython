# test_modeluser.py
from models.users import User

def main():
    # Thử xoá user 'alice' nếu đã tồn tại (bỏ qua lỗi nếu không có)
    try:
        conn = User.register  # chỉ để import cho khớp model
    except:
        pass

    # Đăng ký user mới
    try:
        u = User.register('alice', 'Secr3t!')
        print("Đăng ký thành công:", u)
    except ValueError as e:
        print("Lỗi đăng ký:", e)
        # Nếu user đã có, tải lại từ DB
        u = User.find_by_username('alice')
        print("Đã load sẵn:", u)

    # Tìm và xác thực
    f = User.find_by_username('alice')
    if not f:
        print("Không tìm thấy alice sau khi đăng ký!")
        return

    ok = f.check_password('Secr3t!')
    not_ok = f.check_password('wrong')

    print("check_password('Secr3t!') ->", ok)
    print("check_password('wrong') ->", not_ok)

    assert ok is True, "Mật khẩu đúng nhưng check_password trả về False"
    assert not_ok is False, "Mật khẩu sai nhưng check_password trả về True"
    print("✅ Tất cả test đều pass.")

if __name__ == '__main__':
    main()
