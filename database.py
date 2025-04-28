import pyodbc
from config import CONN_STR

#Hàm get_conn() trả về một pyodbc.Connection.
def get_conn():
    """
    Tra ve mot ket noi pyodbc da cau hinh san toi SQL Server
    """
    return pyodbc.connect(CONN_STR, autocommit=True)