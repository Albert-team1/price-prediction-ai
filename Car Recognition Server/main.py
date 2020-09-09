from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

'''
Temporary profile,m change, update, delete make
'''
app = Flask(__name__)
app.secret_key = "hello" # needed to encrypt and decrypt data
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#app.permanent_session_lifetime = timedelta(minutes=5)

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

    def __init__(self, name, make, model, year, color, condition):
            
        self.name = name
        self.make = make
        self.model = model
        self.year = year
        self.color = color
        self.condition = condition
        
@app.route("/")
def home():
    return render_template("index.html", content="Testing") #

@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        #session.permanent = True   
        user = request.form["nm"]
        session["user"] = user

        found_user = users.query.filter_by(name=user).first() # query database looking for username, user return with first entry
        if found_user:
            session["make"] = found_user.make
            session["model"] = found_user.model
            session["year"] = found_user.year
            session["color"] = found_user.color
            session["condition"] = found_user.condition     
        else:
            usr = users(user, "", "", "", "", "")   # instantiating user
            db.session.add(usr) # staging area, not commit, roll back to previous version of database
            db.session.commit()         
        flash("Login Successful")       
        return redirect(url_for("user"))
    else:
        if "user" in session:  
            flash("Already Logged In!")     
            return redirect(url_for("user"))
            
        return render_template("login.html")

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all()) # list all the 
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
            found_user = users.query.filter_by(name=user).first()
            found_user.make = make # updating user make
            found_user.model = model 
            found_user.year = year
            found_user.condition = condition
            found_user.color = color 
            db.session.commit()                     
            flash("Car Properties were saved")
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
    
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)