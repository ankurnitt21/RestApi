import set_credentials_in_env_variable
import psycopg2.pool
import os

# Make a pool of connection so that you'll not require to make/close the connection again and again
# This method is faster, and it'll fetch the data on runtime from database

pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=os.environ.get('DB_HOST'),
    database=os.environ.get('DB_DATABASE'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    port=os.environ.get('DB_PORT')
)
