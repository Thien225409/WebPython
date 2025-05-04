from typing import Optional
from database import get_conn
from datetime import datetime

class PasswordResetToken:
    """
    Lớp ORM đơn giản cho bảng dbo.PasswordResetTokens:
    - Token: varchar(64) PRIMARY KEY
    - UserID: INT FOREIGN KEY dbo.Users(UserID)
    - ExpiresAt: DATETIMEOFFSET
    """
    @classmethod
    def create(cls, token: str, user_id: int, expires_at: datetime) -> None:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO dbo.PasswordResetTokens (Token, UserID, ExpiresAt) VALUES (?, ?, ?);",
            (token, user_id, expires_at)
        )
        conn.close()
    
    @classmethod
    def get(cls, token: str) -> Optional[dict]:
        conn = get_conn()
        cur = conn.cursor()
        row = cur.execute(
            "SELECT UserID, ExpiresAt FROM dbo.PasswordResetTokens WHERE Token = ?;",
            (token,)
        ).fetchone()
        conn.close()
        if not row:
            return None
        user_id, expires = row.UserID, row.ExpiresAt
        return {'user_id': user_id, 'expires_at': expires}
    @classmethod
    def delete(cls, token: str) -> None:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM dbo.PasswordResetTokens WHERE Token = ?;",
            (token,)
        )
        conn.close()