# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)


app.secret_key = 'password'

app.config['MYSQL_HOST'] = 'sundevilstocksdb.cr82ako04zgl.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'root'  # RDS master username
app.config['MYSQL_PASSWORD'] = 'password123!'  # RDS password
app.config['MYSQL_DB'] = 'sundevilstocksdb'  # RDS database name


print("Database host:", app.config['MYSQL_HOST'])
print("Database user:", app.config['MYSQL_USER'])
print("Database name:", app.config['MYSQL_DB'])



mysql = MySQL(app)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])  # Changed to '/login' to match the form action
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']  # Use 'email' to match the form
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE Email = %s', (email,))
        account = cursor.fetchone()
        if account and check_password_hash(account['CustPass'], password):
            session['loggedin'] = True
            session['id'] = account['CustomerID']
            session['username'] = account['FullName']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)
    

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    print("Form data:", request.form)
    msg = ''
    if request.method == 'POST':
        full_name = request.form['FullName']
        email = request.form['Email']
        password = request.form['CustPass']
        confirm_password = request.form['confirmCustPass']

        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif password != confirm_password:
            msg = 'Passwords do not match!'
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM customer WHERE Email = %s', (email,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                hashed_password = generate_password_hash(password)
                cursor.execute('INSERT INTO customer (FullName, Email, CustPass) VALUES (%s, %s, %s)', (full_name, email, hashed_password))
                mysql.connection.commit()
                cursor.close()
                return redirect(url_for('login'))  # Redirect to the login route
        cursor.close()
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


@app.route('/trade')
def trade():
    # Your code to pass data to the 'trade.html' template
    return render_template('trade.html')

@app.route('/products')
def products():
    return render_template('products.html')



if __name__ == '__main__':
    app.run(debug=True)

