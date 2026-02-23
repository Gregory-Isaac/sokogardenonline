#import flask and its components
from flask import *

import os

#import pymysql module
import pymysql

#create a flask app and give it a name
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'Static/Images'



#below is the sign up route
@app.route("/api/signup", methods=["POST"])
def signup():
    if request.method == "POST":
        #Extract the differnt different details entered on the form 
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        #by use of the print function lets print all those details sent with the upcoming request
        #print(username, email, password, phone)
        #establish aconnection between flask and mysql
        Connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenonline")
        #create a cursor object to execute sql queries
        cursor = Connection.cursor()
        #structure the sql query to insert the data into the database
        sql="INSERT INTO users (username, email, password, phone) VALUES (%s, %s, %s, %s)"
        #create a tuple that will hold the date gotten from the form
        data = (username, email, password, phone)
        #by use of the cursor, execute the sql as you replace the placeholder with the actual values
        cursor.execute(sql, data)
        #commit the changes to the database
        Connection.commit()
        return jsonify({"message": "user registered successfully!"})
         
#below is the login/sign in route
@app.route("/api/signin", methods=["POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"] 
        #by use of the print function lets print all those details sent with the upcoming request
        #print(email, password)
        #establish aconnection between flask and mysql
        Connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenonline")
        #create a cursor object to execute sql queries
        cursor = Connection.cursor()
        #structure the sql query to select the data from the database
        sql="SELECT * FROM users WHERE email=%s AND password=%s"
        #create a tuple that will hold the date gotten from the form
        data = (email, password)
        #by use of the cursor, execute the sql as you replace the placeholder with the actual values
        cursor.execute(sql, data)
        #fetch one record from the database that matches the query
        user = cursor.fetchone()
        #if row there are return it means the password and email are correct othrwise it means they are wrong
        if user is None:
            return jsonify({"message": "login failed!"})
        else:
            return jsonify({"message": "user signed in successfully!", "user":user})


# Below is the route for adding products
@app.route("/api/add_product", methods=["POST"])
def add_product():
    if request.method == "POST":
        #extract the data entered on the form
        product_name = request.form["product_name"]
        product_description = request.form["product_description"]
        products_cost = request.form["products_cost"]
        #for the products photo we shall fetch it from the files as shown below
        products_photo = request.files["products_photo"]

        #extract the file name of the product photo
        photo_path = os.path.join(app.config["UPLOAD_FOLDER"], products_photo.filename)

        #save the products photo image into the new location
        products_photo.save(photo_path)

        #print them out to test whether you are receiving the details sent with the request
        #print(product_name, product_description, products_cost, products_photo)

        

        connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenonline")

        #create a cursor
        cursor = connection.cursor()


        #structure the sql query to insert the data into the database
        sql = "INSERT INTO product_details(product_name, product_description, product_cost, product_photo) VALUES (%s, %s, %s, %s)"

        #create a tuple that will hold the data gotten from the form
        data = (product_name, product_description, products_cost, products_photo)

        # use the cursor to execute the sql as you replace the placeholder with the actual values
        cursor.execute(sql, data)

        #commit the changes to the database
        connection.commit()




        return jsonify({"message": "product added successfully!"})

# print
#below is then route for fetching products
@app.route("/api/get_products", methods=["GET"])
def get_products():
    #create a connection to db
    connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenonline")
    #create a cursor
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    # structure the query to fetch all the products from the table product_details
    sql = "SELECT * FROM product_details"
    #execute the query
    cursor.execute(sql)
    #create a variable that hold the data fetched from the table
    products = cursor.fetchall()

    return jsonify( products)



#run the application
app.run(debug=True)