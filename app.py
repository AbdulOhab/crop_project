from flask import Flask, request, render_template, url_for,flash
from flask import request,redirect,session
from pymongo import MongoClient
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import bcrypt


client = MongoClient("mongodb+srv://admin:admin@cluster0.krz6igk.mongodb.net/retryWrites=true&w=majority")
db = client.get_database('crop_project')
records = db.register

data = client['crop_project']
coll = data['register']


app = Flask(__name__)
app.secret_key = "testing"
authorization_code = "abs"

@app.route('/')
def index():
    return render_template("home.html")


# ErrorHandler
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.errorhandler(502)
def page_not_found(e):
    return render_template("502.html"), 502

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


#assign URLs to have a particular route
@app.route("/signup", methods=['Post', 'GET'])
def signup():
    message = ''
    #if method post in index
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("name")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        authorization = request.form.get("accept")
        #if found in database showcase that it's found
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'Username already used'
            return render_template('signup.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('signup.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('signup.html', message=message)
        if authorization_code != authorization:
            message = 'Wrong Authorization Code!'
            return render_template('signup.html', message=message)
        else:
            #hash the password and encode it
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            #assing them in a dictionary in key value pairs
            user_input = {'name': user, 'email': email, 'password': hashed}
            #insert it in the record collection
            records.insert_one(user_input)

            #find the new created account and its email
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            #if registered redirect to logged in as the registered user
            message = 'Your Account Creation Request Successfully!!'
            return render_template('signup.html', message=message)
    return render_template('signup.html')


@app.route("/login", methods=["POST", "GET"])
#[Get("login")]
def login():
    message = 'Please login to your account!'
    if "email" in session:
        return redirect(url_for("logged_in"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
     
        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


# data = client['crop_project']
# coll = db['register']

data2 = client['test']
coll2 = data2['train']

@app.route('/logged_in')
def logged_in():
    data = coll.find()
    data2 = coll2.find().sort('_id', -1).limit(10)
    inc = 1
    # return render_template("test.html", data = data, inc = inc, data2 = data2)
    if "email" in session:
        email = session["email"]
        message = 'You have successfully logged in!'
        return render_template('indexMain.html', email=email, message=message, data = data, inc = inc, data2 = data2)
    else:
        return redirect(url_for("login"))


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        message = ' You are successfully logged out!'
        return render_template("home.html", message=message)
    else:
        return render_template('login.html')

import pymongo

# data = client['crop_project']
# coll = db['register']



@app.route('/test')
def test():
    data = coll.find()
    data2 = coll2.find()
    inc = 1
    return render_template("test.html", data = data, inc = inc, data2 = data2)

if __name__ == "__main__":
  app.run(debug=True, host='0.0.0.0', port=5000)


