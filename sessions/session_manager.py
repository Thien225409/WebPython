import os
import json
import uuid
from datetime import datetime, timedelta

# Đường dẫn file lưu session
SESSION_FILE = os.path.join(os.path.dirname(__file__), 'sessions.json')
_sessions = {}

#Tải sessions từ file
def _load_sessions():
    global _sessions
    # Nếu file chưa tồn tại, khơỉ tạo sesions rỗng
    if not os.path.exists(SESSION_FILE):
        _sessions = {}
        return
    # Nếu file trống hoặc JSON sai định dạng, cũng khởi tạo sessions rỗng
    try:
        with open(SESSION_FILE, 'r') as f:
            _sessions = json.load(f)
    except (json.JSONDecodeError, ValueError):
        _sessions = {}

# Lưu sessions vào file
def _save_sessions():
    with open(SESSION_FILE, 'w') as f:
        json.dump(_sessions, f)

# Tạo session mới, trả về session_id
def create_session(user_id: int) -> str:
    _load_sessions()
    sid = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=1)  # Session expires in 1 hour
    _sessions[sid] = {
        'user_id': user_id,
        'created_at': datetime.utcnow(),
        'expires_at': expires_at,
        # Khi login, controller sẽ thêm 'csrf_token' vào đây
    }
    _save_sessions()
    return sid

# Lấy session theo session_id
def get_session(sid: str) -> dict | None:
    session = _sessions.get(sid)
    if session:
        if session['expires_at'] < datetime.utcnow():
            delete_session(sid)  # Xóa session hết hạn
            return None
        return session
    return None  # Session không tồn tại

# Xóa session
def delete_session(sid: str):
    _load_sessions()
    if sid in _sessions:
        del _sessions[sid]
        _save_sessions()