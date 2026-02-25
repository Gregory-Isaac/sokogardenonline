# app.py
from flask import Flask, request, jsonify
import pymysql
from datetime import datetime

app = Flask(__name__)

# Database connection
def get_db_connection():
    return pymysql.connect(host='localhost',user='root',password='', database='packagedfood',cursorclass=pymysql.cursors.DictCursor)

# ------------------- ROUTES -------------------

# 1. Get all packaged foods
@app.route('/api/packagedfood', methods=['GET'])
def get_all_foods():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM packagedfood")
    foods = cursor.fetchall()
    conn.close()
    return jsonify(foods)

# 2. Get a single food by ID
@app.route('/api/packagedfood/<int:id>', methods=['GET'])
def get_food(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM packagedfood WHERE id=%s", (id,))
    food = cursor.fetchone()
    conn.close()
    if food:
        return jsonify(food)
    return jsonify({"message": "Food item not found"}), 404

# 3. Add a new food item
@app.route('/api/packagedfood', methods=['POST'])
def add_food():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO packagedfood (name, brand, weight, unit, expiry, price, stock, photo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (
            data['name'],
            data['brand'],
            data['weight'],
            data['unit'],
            datetime.strptime(data['expiry'], '%Y-%m-%d').date(),
            data['price'],
            data['stock'],
            data.get('photo', None)
        ))
        conn.commit()
        return jsonify({"message": "Food item added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

# 4. Update a food item
@app.route('/api/packagedfood/<int:id>', methods=['PUT'])
def update_food(id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        UPDATE packagedfood
        SET name=%s, brand=%s, weight=%s, unit=%s, expiry=%s, price=%s, stock=%s, photo=%s
        WHERE id=%s
    """
    try:
        cursor.execute(query, (
            data['name'],
            data['brand'],
            data['weight'],
            data['unit'],
            datetime.strptime(data['expiry'], '%Y-%m-%d').date(),
            data['price'],
            data['stock'],
            data.get('photo', None),
            id
        ))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"message": "Food item not found"}), 404
        return jsonify({"message": "Food item updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

# 5. Delete a food item
@app.route('/api/packagedfood/<int:id>', methods=['DELETE'])
def delete_food(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM packagedfood WHERE id=%s", (id,))
    conn.commit()
    if cursor.rowcount == 0:
        return jsonify({"message": "Food item not found"}), 404
    conn.close()
    return jsonify({"message": "Food item deleted successfully"})

# ------------------- RUN APP -------------------
if __name__ == '__main__':
    app.run(debug=True)