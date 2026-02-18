#import flask and its components
from flask import *

#import pymysql module
import pymysql

#create a flask app and give it a name
app = Flask(__name__)


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
         










#run the application
app.run(debug=True)