# Using this to test the database connection.
from db_connect import get_connection

conn = get_connection()
if conn:
    print("Connection successful!")
    conn.close()
else:
    print("Connection failed.")