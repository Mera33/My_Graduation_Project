from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from firebase_admin import credentials, db, initialize_app
from util import *


cred = credentials.Certificate('georgeproject-8d253-firebase-adminsdk-ks87y-ee3cfe886c.json')
initialize_app(cred, {
    'databaseURL': 'https://georgeproject-8d253-default-rtdb.europe-west1.firebasedatabase.app/'
})


app = Flask(__name__)



app.config['UPLOAD_FOLDER'] = '/'
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.after_request
def after_request(response):
    """No Cache"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':

        # If the user is already logged in, he/she will be automatically redirected to the homepage
        if session.get('user_id'):
            return redirect('/')
        else:
            return render_template("SignIn.html")
    else:

        # Requesting User information from a given email
        user = User.get_from_email(convert_email(request.form.get("email")))
        f = request.form

        # User Error Checking
        if user is None or None in [f.get('password'), f.get('email')] or '' in [f.get('password'), f.get('email')] or request.form.get("password") != user.details["password"]:
            return render_template('SignIn.html', error="Please Check Your Username and Password")
 

        # Logging in and redirecting to the homepage
        session['user_id'] = request.form.get("email")
        return redirect('/')


@app.route('/')
def index():
    return render_template("Home.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("SignUp.html")
    else:
        f = request.form

        # User Error Checking
        if None in [f.get(attribute) for attribute in ["email", "username", "password"]] or '' in [f.get(attribute) for attribute in ["email", "username", "password"]] or User.get_from_email(convert_email(request.form.get('email'))) is not None:
            return render_template("SignUp.html", error="There is an existing account with this email")


        # Creating a user object with the given information
        user = User(
            convert_email(request.form.get('email')),
            username=request.form.get('username'),
            password=request.form.get('password')
            )
        

        # Adding the new user to the database
        user.add()

        # Logging in automatically
        session["user_id"] = request.form.get("email")

        # Redirecting the user to the homepage
        return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/talk')
def talk():
    return render_template("Specialists.html")


@app.route('/dna', methods = ["GET", "POST"])
@login_required
def dna():
    if request.method == "GET":
        return render_template('DNA.html')
    
    else:
        sequence = request.form.get("sequence").upper()
        print(sequence)
        if sequence is None or len(sequence) != 512:
            return render_template('DNA.html', error="The sequence is not valid. Your sequence should only contain (A, T, C, G) letters uppercased, length must be 512.")
        
        if predict(sequence) is None:
            return render_template('DNA.html', error="The sequence is not valid. Your sequence should only contain (A, T, C, G) letters uppercased, length must be 512.")

        
        return render_template('DNA.html', show=True, type=predict(sequence))


@app.route('/about')
def about():
    return render_template('AboutUs.html')   


class User:
    def __init__(self, email, **kwargs):
        self.details = kwargs
        self.email = email


    def add(self):
        """
        Adds the current User to the database
        """
        ref = db.reference('User')
        ref.update({
            self.email: self.details
        })


    @classmethod
    def get_from_email(cls, email):
        """
        Returns a User object with the information of the user with a given email address
        """
        ref = db.reference(f'User/{email}')
        if ref.get() is None:
            return None
        return User(
            email,
            **ref.get()
        )

