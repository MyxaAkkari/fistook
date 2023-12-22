from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os
from datetime import datetime

app = Flask(__name__)
users = [] # Holds the users information
USERS = "users.txt" # users file
app.secret_key = os.urandom(24) # Genreating a random 24bit key

# Loads the users info from file to list
def load_data():
    global users
    with open(USERS, 'r') as filehandle:
        users = json.load(filehandle)

# Save users list to users.txt file
def save_2_file():
    with open(USERS, 'w') as filehandle:
        json.dump(users, filehandle, indent=2)

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        user = next((usr for usr in users if usr['id'] == user_id), None)
        last_login_time = user.get('last_login_time', 'N/A')
        return render_template('index.html', last_login_time=last_login_time)
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global users
    if request.method == 'GET': # if method is GET show the login page without error messages
        no_email = ""
        wrong_password = ""
        return render_template('login.html', no_email=no_email, wrong_password=wrong_password)
    else:
        email_uname = request.form["email"]
        password = request.form["password"]
        no_email = "Email or Username not found, Please register." # error message

        for usr in users: # loop in users list
            if email_uname == usr["email"] or email_uname == usr["username"]: # check if email/ Uname exist in list
                if password == usr["password"]:
                    session['user_id'] = usr['id']  # Save user ID in session
                    usr['last_login_time'] = datetime.now().strftime('%d-%m-%Y %H:%M')
                    flash(f"Welcome, {usr['username']}!") # welcome message using flash
                    save_2_file()  # save updated users list to file
                    return redirect(url_for('index'))  # Redirect to the index route
                else:
                    wrong_password = 'Incorrect email or password. <a href="/passreset">Forgot Password?</a>' # error message contains a link for pwd reset page
                    return render_template('login.html', wrong_password=wrong_password) #reload login.html with error message

        return render_template('login.html', no_email = no_email) ##reload login.html with error message 

@app.route('/register', methods=['GET', 'POST'])
def register():
    global users
    if request.method == 'GET': # if method is GET show the register page without error messages
        short_password = ""
        email_exist = ""
        return render_template('register.html')
    else:
        #take new email/Uname/pwd
        new_uname = request.form["new_uname"]
        new_email = request.form["new_email"]
        new_password = request.form["new_password"]
        short_password = "Password must be 8 chars or more." # error message
        email_exist = "Email Already registered." # error message

        for usr in users: # loop through list to check if email already exists
            if new_email == usr["email"]:
                return render_template('register.html', email_exist = email_exist)
        if len(new_password) < 8: # check if pwd meets requirements
            return render_template('register.html', short_password = short_password)
        else: # if all successfull 
            user_id = len(users) + 1  # Generate a simple user ID
            users.append({"id": user_id, "username": new_uname, "email": new_email, "password": new_password,
                          "last_login_time": datetime.now().strftime('%%d-%m-%Y %H:%M')})  # add new user info to list
            session['user_id'] = user_id  # Save user ID in session
            save_2_file() # save updated users list to file
            flash(f"Welcome, {new_uname}!") # welcome message
            return redirect(url_for('index'))  # Redirect to the index route

@app.route('/passreset')
def passreset(): # in progress
    return render_template('passreset.html')

@app.route('/logout', methods = ["POST"])
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('index'))

if __name__ == "__main__":
    load_data() # load data on startup 
    app.run(debug=True, port=8000) # run the app with debug mode on port 8k
