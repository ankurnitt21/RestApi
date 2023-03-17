from Postgres_Conn import conn

# Test the connection
try:
    cur = conn.cursor()
    print("Connection successful!")
except:
    print("Connection failed.")
finally:
    cur.close()
    conn.close()

