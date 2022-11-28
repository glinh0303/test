import cgi
import MySQLdb.cursors
from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'any secret string'
    # Configure db
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'project'

mysql = MySQL(app)

bcrypt = Bcrypt(app)


class RegisterForm(FlaskForm):
    firstName = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder" : "First Name"})
    lastName = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder" : "Last Name"})
    address = StringField(validators=[InputRequired(), Length(min=4, max=250)], render_kw={"placeholder" : "Address"})
    phone = IntegerField(validators=[InputRequired()], render_kw={"placeholder" : "Phone"})
    email = EmailField(validators=[InputRequired()], render_kw={"placeholder" : "Email"})
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder" : "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField(label="Register")

    # def validate_username(self, username):
    #     from sqlalchemy.testing.pickleable import User
    #     existing_user_user_name = User.query.filter_by(username=username.data).first()
    #     if existing_user_user_name:
    #         raise ValidationError("That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
        username = StringField(validators=[InputRequired(), Length(
            min=4, max=20)], render_kw={"placeholder": "Username"})
        password = PasswordField(validators=[InputRequired(), Length(
            min=4, max=20)], render_kw={"placeholder": "Password"})

        submit = SubmitField(label="Login")


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

# @app.route('/',  methods=['GET'])
# def getvalue():
#     userDetails = request.form
#     username = userDetails['username']
#     password = userDetails['password']
#     return render_template('test.html', user=username,p=password)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    # form = cgi.FieldStorage()
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        print("helloooooooooooooooooooo")
        # Fetch form data
        userDetails = request.form
        username = userDetails['username']
        print(username,"-------------------")
        password = userDetails['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users_details WHERE username = %s AND password = %s", (username, password))
        account = cur.fetchone()
        if form.validate_on_submit():
            if account:
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # session['lastName'] = account['lastName']
                # msg = 'Logged in successfully!'
                # return redirect(url_for('home_page', msg=msg))
                flash(f'Logged in successfully!', category='success')
                return redirect(url_for('home_page'))
                # return render_template('login.html', msg=msg)
            else:
                msg = 'Incorrect username / password !'
                # return render_template('home.html', msg=msg)
                return redirect(url_for('login', msg=msg))
        # mysql.connection.commit()
        # cur.close()

        # return 'success'
        # if form.validate_on_submit():
        #     return redirect(url_for('home'))

    return render_template('login.html', form=form)
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    msg = ''
    if request.method == 'POST' and 'username' in request.form:
        # Fetch form data
        userDetails = request.form
        # lastName = userDetails['lastName']
        # firstName = userDetails['firstName']
        # address = userDetails['address']
        phone = userDetails['phone']
        email = userDetails['email']
        username = userDetails['username']
        password = userDetails['password']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users_details WHERE username = %s ", (username,))
        account = cur.fetchone()
        if account:
            msg = 'Account already exists !'
            return redirect(url_for('register', msg=msg))
        else:
            cur.execute("INSERT INTO users_details(phone, email, username, password) VALUES(%s, %s, %s, %s)", (phone, email, username, password))
            mysql.connection.commit()
            # cur.close()
            # msg = 'You have successfully registered !'
            return redirect(url_for('login'))
        # return "success"
    # if form.validate_on_submit():
    #     hashed_password = bcrypt.generate_password_hash(form.password.data)
    #     new_user = User(username=form.username.data, password=hashed_password)
    #     return redirect(url_for('login'))

    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)