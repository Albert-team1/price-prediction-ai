from flask import Flask, redirect, url_for, render_template, request, session, flash
#from datetime import timedelta
#from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
#import tensorflow as tf

import pickle 
import os
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'static/uploads/' 

make_prices = pd.read_csv('manufacturer_prices.txt', sep='\t')
make_counts = pd.read_csv('manufacturer_counts.txt', sep='\t')
color_counts = pd.read_csv('paint_color_counts.txt', sep='\t')
color_prices = pd.read_csv('paint_color_prices.txt', sep='\t')
condition_prices = pd.read_csv('condition_prices.txt', sep='\t')
condition_counts = pd.read_csv('condition_counts.txt', sep='\t')

labels = pd.read_csv('labels.csv')

data_model = None
file_name = "model_file.p"
with open(file_name, 'rb') as pickled:
    x = pickle.load(pickled)
    data_model = x['model']

app = Flask(__name__)
app.secret_key = "hello" # needed to encrypt and decrypt data
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
#app.permanent_session_lifetime = timedelta(minutes=5)

'''
db = SQLAlchemy(app)
# close browser, session data is deleted
class users(db.Model):
    
    _id = db.Column("id", db.Integer, primary_key=True)    # needs to have primary key, unique identifier
    name = db.Column("name", db.String(100)) # if name is not defined in first parameter, use variable name
    make = db.Column("make", db.String(100)) # probably the case do quick sql alchemy tutorial
    model = db.Column("model", db.String(100))
    year = db.Column("year", db.String(100))
    color = db.Column("color", db.String(100))
    condition = db.Column("condition", db.String(100))
    prediction = db.Column("prediction", db.Float())
    
    def __init__(self, name, make, model, year, color, condition, prediction):
            
        self.name = name
        self.make = make
        self.model = model
        self.year = year
        self.color = color
        self.condition = condition
        self.prediction = prediction
'''
@app.route("/predict/<filename>")
def predict(filename):
    
    if "user" in session == False:
        flash("You are not logged in!")     
        return redirect(url_for("login"))
    
    '''
    PLEASE ADD TF MODEL REQUEST CODE HERE
    '''
 
    user = session["user"]
    year = str(session["year"])
    make = str(session["make"])
    condition = str(session["condition"])
    paint_color = str(session["color"])

    age = 2021 - int(year)
    make_median_price = make_prices[make_prices.make == make.lower()]['price']
    make_count = make_counts[make_counts.make == make.lower()]['count']
    condition_median_price = condition_prices[condition_prices.condition == condition.lower()]['price']
    condition_count = condition_counts[condition_counts.condition == condition.lower()]['count']
    color_median_price = color_prices[color_prices.paint_color == paint_color.lower()]['price']
    color_count = color_counts[color_counts.paint_color == paint_color.lower()]['count']

    entry = [age, make_median_price, condition_median_price, color_median_price, make_count, condition_count, color_count]
    entry = np.array(entry)
    entry = entry.reshape(1, -1)
    prediction = round(data_model.predict(entry)[0])

    '''
    found_user = users.query.filter_by(name=user).first()
    found_user.prediction = prediction 
    db.session.commit()
    '''
    return render_template("predict.html", prediction=prediction, filename=filename)
    

@app.route("/")
def home():
    return render_template("index.html", content="Testing") #

@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        #session.permanent = True   
        user = request.form["nm"]
        session["user"] = user

        #found_user = users.query.filter_by(name=user).first() # query database looking for username, user return with first entry
        #if found_user:
          
        #else:
        #   pass
        #    usr = users(user, "", "", "", "", "", 0.0)   # instantiating user
        #    db.session.add(usr) # staging area, not commit, roll back to previous version of database
        #    db.session.commit()         
        flash("Login Successful")       
        return redirect(url_for("user"))
    else:
        if "user" in session:  
            flash("Already Logged In!")     
            return redirect(url_for("user"))
            
        return render_template("login.html")

'''
@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all()) # list all the 
'''
@app.route("/user", methods=["POST", "GET"])
def user():
    
    make = None # change to empty string
    model = None
    year = None
    color = None
    condition = None
    if "user" in session.keys():
        user = session["user"]
        if request.method == "POST":
            make = request.form["make"]
            model = request.form["model"]
            year = request.form["year"]
            condition = request.form["condition"]
            color = request.form["color"]
            session["make"] = make
            session["model"] = model
            session["year"] = year
            session["condition"] = condition
            session["color"] = color
            '''
            found_user = users.query.filter_by(name=user).first()
            found_user.make = make # updating user make
            found_user.model = model 
            found_user.year = year
            found_user.condition = condition
            found_user.color = color 
            db.session.commit() 
            '''                    
            flash("Car Properties were saved")

            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for("predict", filename=filename))
        else:
            if "make" in session and "model" in session and "year" in session and "color" in session and "condition" in session:
                make = session["make"]
                model = session["model"]
                year = session["year"]
                color = session["color"]
                condition = session["condition"]

        return render_template("user.html", user=user, make=make, model=model, year=year, color=color, condition=condition)
    else:
        flash("You are not logged in!")     
        return redirect(url_for("login"))
        
@app.route("/logout")
def logout():

    #user = session["user"]
    flash("You have been logged out", "info")       
    session.pop("user", None)
    session.pop("make", None)
    session.pop("model", None)
    session.pop("year", None)
    session.pop("condition", None)
    session.pop("color", None)
    # flash("You have been logged out!", "info")    # built in ones, warning info and error
    return redirect(url_for("login"))

@app.route('/display/<filename>')
def display_image(filename):

    return redirect(url_for('static', filename='uploads/' + filename), code=301)    
    
if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True)