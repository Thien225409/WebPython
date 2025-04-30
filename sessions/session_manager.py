from database import get_conn
import uuid
from datetime import datetime, timedelta, timezone
from config import SESSION_TTL_HOURS

# Tạo session mới, trả về session_id
def create_session(user_id: int) -> str:
    session_id = str(uuid.uuid4()) # Tạo session id
    
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    expire_iso = (now + timedelta(hours=SESSION_TTL_HOURS)).isoformat()

    
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dbo.Sessions (SessionId, UserId, CreatedAt, ExpiresAt) VALUES (?, ?, ?, ?)",
            (session_id, user_id, now_iso, expire_iso)
        )
    return session_id
# Xóa session
def delete_session(sid: str):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM dbo.Sessions WHERE SessionId = ?",
            sid
        )

def get_session(sid: str):
    """
    Lấy thông tin phiên (session) từ session_id.

    Tham số:
        sid (str): Mã định danh phiên do server tạo (UUID).

    Trả về:
        dict: {
            'user_id': int,          # ID người dùng
            'create_at': str,        # ISO timestamp khi tạo phiên
            'expires_at': str        # ISO timestamp khi hết hạn
        } nếu session tồn tại và còn hạn.
        None: nếu session không tồn tại hoặc đã hết hạn (khi hết hạn, session cũng được xóa).
    """
    with get_conn() as conn:
        cursor = conn.cursor()
        row = cursor.execute(
            """
            SELECT UserId,
                CONVERT(varchar(33), CreatedAt, 126),
                CONVERT(varchar(33), ExpiresAt, 126)
            FROM dbo.Sessions
            WHERE SessionId = ?
            """,
            sid
        ).fetchone()
    if not row:
        return None
    user_id, created, expires = row
    if datetime.fromisoformat(expires) < datetime.now(timezone.utc):
        delete_session(sid)
        return None
    session_dict = {
        'session_id': sid,
        'user_id': user_id,
        'create_at': created,
        'expires_at': expires
    }
    return session_dict