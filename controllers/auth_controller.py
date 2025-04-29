import time
from models.users import User
from utils.template_engine import render_template
from sessions import session

# Đăng kí người dùng 
def register(request):
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Kiểm tra nếu user đã tồn tại
        try:
            user = User.register(username, password)
        except ValueError as e:
            return str(e), 400
        
        return "Đăng kí thành công", 200
    
    return render_template('register.html') # Hiểm thị form đăng kí
# Đăng nhập người dùng
def login(request):
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Truy vaan trong co so du lieu
        user = User.find_by_username(username)
        if user and user.check_password(password):
            # Lưu thông tin người dùng vào session
            session['user_id'] = user.user_id
            return "Đăng nhập thành công", 200
        
        return "Thông tin đăng nhập không chính xác", 400
    
    return render_template('login.html')

# Đăng xuất người dùng
def logout(request):
    session.pop('user_id', None)
    return "Đã đăng xuất", 200