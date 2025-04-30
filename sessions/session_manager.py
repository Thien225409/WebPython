import os
import json
import uuid
from datetime import datetime, timedelta

# Đường dẫn file lưu session
SESSION_FILE = os.path.join(os.getcwd(), 'sessions.json')
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
    now_iso = datetime.utcnow().isoformat()
    expire_iso = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    _sessions[sid] = {
        'user_id': user_id,
        'create_at': now_iso,
        'expires_at': expire_iso
    }
    _save_sessions()
    return sid

def get_session(sid: str):
    _load_sessions()
    s = _sessions.get(sid)
    if not s:
        return None
    # So s['expires_at'] là chuỗi ISO → parse bằng fromisoformat
    if datetime.fromisoformat(s['expires_at']) < datetime.utcnow():
        delete_session(sid)
        return None
    return s

# Xóa session
def delete_session(sid: str):
    _load_sessions()
    if sid in _sessions:
        del _sessions[sid]
        _save_sessions()