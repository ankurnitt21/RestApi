import psycopg2

# Replace <username>, <password>, <host>, <port>, and <database> with your own values
conn = psycopg2.connect(
    host="<host>",
    port="<port>",
    database="<database>",
    user="<username>",
    password="<password>"
)
