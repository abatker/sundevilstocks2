# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, current_app
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
import random
import hashlib

scheduler = BackgroundScheduler()




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

##########################################################################################################################

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        # User login
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM customer WHERE Email = %s', [email])
            account = cursor.fetchone()
            if account and check_password_hash(account['CustPass'], password):
                session['loggedin'] = True
                session['id'] = account['CustomerID']
                session['username'] = account['FullName']
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect username/password!'
        # Admin login
        elif 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM admin WHERE Name = %s', [username])
            admin = cursor.fetchone()
            if admin:
                admin_hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if admin['AdminPass'] == admin_hashed_password:
                    session['loggedin'] = True
                    session['id'] = admin['AdminID']
                    session['username'] = admin['Name']
                    session['admin'] = True  # Set a session variable for admin
                    return redirect(url_for('admin_dashboard'))
                else:
                    msg = 'Incorrect admin username/password!'
            else:
                msg = 'Admin account not found!'
    return render_template('login.html', msg=msg)

@app.route('/admin_dashboard')
def admin_dashboard():
    # Check if admin is logged in
    if 'loggedin' in session and session.get('admin'):
        # Admin is logged in, render the admin dashboard
        return render_template('adminDash.html', username=session['username'])
    # If not an admin or not logged in, redirect to the login page
    return redirect(url_for('login'))

    

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


@app.route('/products')
def products():
    return render_template('products.html')

def change_market_hours():
    if request.method == 'POST':
        new_market_hours = request.form['market-hours']
        
        # Update market hours in the database
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE MarketHours SET hours = %s", (new_market_hours,))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('adminDash'))  # Redirect to the admin dashboard after updating market hours
        except MySQLdb.Error as e:
            # Handle database errors
            error_msg = "Error updating market hours: {}".format(str(e))
            return render_template('error.html', error_msg=error_msg)


@app.route('/change_market_schedule', methods=['POST'])
def change_market_schedule():
    if request.method == 'POST':
        new_market_schedule = request.form['market-schedule']
        
        # Update market schedule in the database
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE MarketSchedule SET schedule = %s", (new_market_schedule,))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('adminDash'))  # Redirect to the admin dashboard after updating market schedule
        except MySQLdb.Error as e:
            # Handle database errors
            error_msg = "Error updating market schedule: {}".format(str(e))
            return render_template('error.html', error_msg=error_msg)

############################################################################################################

def get_random_price_change():
    """Simulate a random price change percentage."""
    return random.uniform(-0.05, 0.05)

def update_stock_prices():
    with app.app_context():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT StockID, CurrentPrice, High, Low FROM stock")
        stocks = cursor.fetchall()
        for stock in stocks:
            change_percent = get_random_price_change()
            new_price = stock['CurrentPrice'] * (1 + change_percent)
            new_high = max(stock['High'], new_price) if stock['High'] else new_price
            new_low = min(stock['Low'], new_price) if stock['Low'] else new_price
            cursor.execute("UPDATE stock SET CurrentPrice = %s, High = %s, Low = %s WHERE StockID = %s",
                           (new_price, new_high, new_low, stock['StockID']))
        mysql.connection.commit()
        cursor.close()

scheduler = BackgroundScheduler()
scheduler.add_job(update_stock_prices, 'interval', minutes=1)

if __name__ == '__main__':
    scheduler.start()  # Start the scheduler
    app.run(debug=True)  # Start Flask app
