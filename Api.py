from flask import Flask, request, jsonify
from Postgres_Conn import pool

# Set up the Flask application
app = Flask(__name__)


# Define a route for creating a new item
@app.route('/items', methods=['POST'])
def create_item():
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
    pool.putconn(conn)
    # Return a JSON response with the new item's ID
    return jsonify({'id': cur.lastrowid}), 201


# Define a route for retrieving all items
@app.route('/itemsall', methods=['GET'])
def get_all_items():
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
    pool.putconn(conn)
    # Return a JSON response with the items
    return jsonify(items)


# Define a route for retrieving a single item by ID
@app.route('/items/<string:name>', methods=['GET'])
def get_item(name):
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
    pool.putconn(conn)
    return jsonify(item)


# Define a route for updating an item by ID
@app.route('/items/<string:name>', methods=['PUT'])
def update_item(name):
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
    pool.putconn(conn)
    # Return a JSON response with the updated item's ID
    return jsonify({'id': name})


# Define a route for deleting an item by ID
@app.route('/itemsdel/<string:name>', methods=['DELETE'])
def delete_item(name):
    conn = pool.getconn()
    cur = conn.cursor()
    # Delete the item with the specified ID from the database
    cur.execute("DELETE FROM items WHERE name = %s", (name,))
    conn.commit()
    pool.putconn(conn)

    # Return a JSON response with the deleted item's ID
    return jsonify({'id': name})


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
