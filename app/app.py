# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)


app.secret_key = 'password'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password123!'
app.config['MYSQL_DB'] = 'sun_devil_stocks'

mysql = MySQL(app)

@app.route('/')
@app.route('/home.html')
def home():
    return render_template('home.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    msg = ''
    return render_template('login.html', msg=msg)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE Email = %s AND CustPass = %s', (email, generate_password_hash(password),))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['CustomerID']
            session['username'] = account['FullName']
            msg = 'Logged in successfully !'
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register.html', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and all(k in request.form for k in ('username', 'password', 'email')):
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE Email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        else:
            cursor.execute('INSERT INTO customer VALUES (NULL, %s, %s, %s)', (username, email, generate_password_hash(password),))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/portfolio.html')
def portfolio():
    return render_template('portfolio.html')

@app.route('/testdb')
def testdb():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT VERSION()")
        version = cur.fetchone()
        cur.close()
        return f"MySQL version: {version[0]}"
    except MySQLdb.Error as e:
        return f"Error: {str(e)}"



if __name__ == '__main__':
    app.run(debug=True)
