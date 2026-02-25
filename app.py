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

 # Mpesa Payment Route/Endpoint 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth


@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
    if request.method == 'POST':
        amount = request.form.get('amount')
        phone = request.form.get('phone')
        
        # Basic validation
        if not amount or not phone:
            return jsonify({"error": "Amount and phone are required"}), 400
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid amount"}), 400
        
        # Format phone (assume Kenyan numbers)
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif not phone.startswith('254'):
            return jsonify({"error": "Invalid phone number"}), 400
        
        # Use environment variables for credentials (recommended for production)
        consumer_key = os.getenv("MPESA_CONSUMER_KEY", "GTWADFxIpUfDoNikNGqq1C3023evM6UH")
        consumer_secret = os.getenv("MPESA_CONSUMER_SECRET", "amFbAoUByPV2rM5A")
        passkey = os.getenv("MPESA_PASSKEY", "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919")
        business_short_code = "174379"
        
        # GENERATING THE ACCESS TOKEN
        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        try:
            r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret), timeout=10)
            r.raise_for_status()
            data = r.json()
            access_token = "Bearer " + data['access_token']
        except requests.RequestException as e:
            return jsonify({"error": "Failed to generate access token", "details": str(e)}), 500
        
        # GETTING THE PASSWORD
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        data_str = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data_str.encode())
        password = encoded.decode('utf-8')
        
        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(int(amount)),  # Use dynamic amount, convert to int for API
            "PartyA": phone,
            "PartyB": business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/api/confirmation.php",
            "AccountReference": "SokoGarden",
            "TransactionDesc": "Payment for products"
        }
        
        # POPULATING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }
        
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            response_data = response.json()
            # Log to database (assuming a payments table with columns: phone, amount, timestamp, status)
            connection = pymysql.connect(host="localhost", user="root", password="", database="sokogardenonline")
            cursor = connection.cursor()
            sql = "INSERT INTO payments (phone, amount, timestamp, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (phone, amount, timestamp, "initiated"))
            connection.commit()
            connection.close()
            return jsonify({"message": "Please complete payment on your phone. We will deliver shortly.", "response": response_data})
        except requests.RequestException as e:
            return jsonify({"error": "Payment request failed", "details": str(e)}), 500

#run the application

app.run(debug=True)