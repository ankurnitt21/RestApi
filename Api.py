import psycopg2
from Oauth import create_oauth
from oauth_config import APP_SECRET_KEY
from flask import Flask, request, jsonify, redirect, url_for, session
from Postgres_Conn import pool
from authlib.integrations.flask_client import OAuth
from datetime import timedelta
from auth_decorator import login_required

app = Flask(__name__)

# Session config
app.secret_key = APP_SECRET_KEY
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

oauth = create_oauth(app)


@app.route('/login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the Google oauth client
    token = google.authorize_access_token()  # Access token from Google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specified in the scope
    user_info = resp.json()
    # user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from Google
    session['profile'] = user_info
    session.permanent = True  # make the session permanent, so it keeps existing after browser gets closed
    return redirect('/itemsall')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


# Define a route for creating a new item
@app.route('/items', methods=['POST'])
def create_item():
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()
        # Get the item data from the request body
        item_data = request.get_json()

        # Insert the new item into the database
        cur.execute(
            "INSERT INTO items (name, description, price) VALUES (%s, %s, %s)",
            (item_data['name'], item_data['description'], item_data['price'])
        )
        conn.commit()

        # Return a JSON response with the new item's ID
        return jsonify({'id': cur.lastrowid}), 201

    except (psycopg2.Error, KeyError) as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 400

    finally:
        if conn:
            pool.putconn(conn)


# Define a route for retrieving all items
@app.route('/itemsall', methods=['GET'])
@login_required
def get_all_items():
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()
        # Retrieve all items from the database
        cur.execute("SELECT * FROM items")
        results = cur.fetchall()

        # Convert the results to a list of dictionaries
        items = []
        for row in results:
            item = {'name': row[0], 'description': row[1], 'price': row[2]}
            items.append(item)

        # Return a JSON response with the items
        return jsonify(items)

    except Exception as e:
        # Handle any exceptions that occur during processing
        return jsonify({'error': str(e)}), 500

    finally:
        # Make sure to always return the connection to the connection pool
        if conn:
            pool.putconn(conn)


# Define a route for retrieving a single item by ID
@app.route('/items/<string:name>', methods=['GET'])
def get_item(name):
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()
        # Retrieve the item with the specified ID from the database
        cur.execute("SELECT * FROM items WHERE name = %s", (name,))
        result = cur.fetchone()

        # If no item was found, return a 404 error
        if result is None:
            return jsonify({'error': 'Item not found'}), 404

        # Convert the result to a dictionary and return it as a JSON response
        item = {'name': result[0], 'description': result[1], 'price': result[2]}
        return jsonify(item)
    except (Exception, psycopg2.DatabaseError):
        return jsonify({'error': 'An error occurred while retrieving the item'}), 500
    finally:
        if conn:
            pool.putconn(conn)


# Define a route for updating an item by ID
@app.route('/items/<string:name>', methods=['PUT'])
def update_item(name):
    conn = None
    try:
        conn = pool.getconn()
        cur = conn.cursor()
        # Get the updated item data from the request body
        item_data = request.get_json()

        # Update the item in the database
        cur.execute(
            "UPDATE items SET name = %s, description = %s, price = %s WHERE name = %s",
            (item_data['name'], item_data['description'], item_data['price'], name)
        )
        conn.commit()
        # Return a JSON response with the updated item's ID
        return jsonify({'id': name}), 200
    except (psycopg2.DatabaseError, Exception) as error:
        # Rollback the transaction if there was an error
        if conn:
            conn.rollback()
        # Return an error response
        return jsonify({'error': str(error)}), 500
    finally:
        if conn:
            # Return the connection to the connection pool
            pool.putconn(conn)


# Define a route for deleting an item by ID
@app.route('/itemsdel/<string:name>', methods=['DELETE'])
def delete_item(name):
    conn = pool.getconn()
    cur = conn.cursor()
    try:
        # Delete the item with the specified ID from the database
        cur.execute("DELETE FROM items WHERE name = %s", (name,))
        conn.commit()
    except:
        # Roll back the transaction if an error occurs
        conn.rollback()
        return jsonify({'error': 'Failed to delete item'}), 500
    finally:
        pool.putconn(conn)

    # Return a JSON response with the deleted item's ID
    return jsonify({'id': name})


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
