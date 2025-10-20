from flask import Flask, render_template, request, redirect, url_for , session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)

app.secret_key = os.getenv('secret_key')

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] =  os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')





mysql = MySQL(app)




@app.route('/')
def index():
    return redirect(url_for('login'))


#signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password'] 

        if password != confirm_password:
            flash('Password and Confirm Password do not match', 'danger')
            return redirect(url_for('signup'))
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        user = cursor.fetchone()

        # check if user already exists
        if user:
            flash('Username or Email already exists', 'danger')
            return redirect(url_for('signup'))
        
        #hash  password
        hashed_password =  generate_password_hash(password)
        
        # insert user into database
        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username,email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash('YOu have successfully created an account', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


#Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()

        

        # check if user exists and password is correct
        if user and check_password_hash(user[3], password):

            session['logged_in'] = True
            session['username'] = user[1]   
            session['user_id'] = user[0]

            flash('You are now logged in', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login crdentials', 'danger')
    return render_template('login.html')

#dashboard route
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')

    

    cursor= mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM products WHERE user_id= %s', (user_id,)) 
    product_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM business WHERE user_id= %s', (user_id,)) 
    business_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM orders WHERE user_id= %s', (user_id,)) 
    order_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM orders WHERE user_id = %s AND status = %s', (user_id, 'pending'))
    pending_orders = cursor.fetchone()[0]

    cursor.close()

    return render_template('dashboard.html', product_count=product_count, business_count=business_count , order_count=order_count, pending_orders=pending_orders) 


                                                                       # PRDUCTS PART

#products route
@app.route('/products')
def products():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM products WHERE user_id = %s', (user_id,))
    products = cursor.fetchall()
    cursor.close()

    return render_template('products.html', products=products)

#add product route
@app.route('/add-route', methods=['GET', 'POST'])
def add_product():

    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        name = request.form['name']
        type = request.form['type']
        description = request.form['description']
        user_id = session.get('user_id')

        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO products (product_name, product_type, product_description, user_id) VALUES (%s, %s, %s, %s)' , (name,type,description, user_id))
        mysql.connection.commit()
        cursor.close()

        flash('Product added successfully', 'success')
        return redirect(url_for('products'))

    return render_template('add_products.html')

#update product route
@app.route('/update-product/<int:product_id>', methods=['GET', 'POST'])
def update_products(product_id):
    if 'logged_in' not in session:
       return redirect (url_for('login'))
    
    user_id = session.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM products WHERE product_id=%s AND user_id=%s ', (product_id ,user_id))
    product= cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        name= request.form['name']
        type = request.form['type']
        description = request.form['description']

        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE products SET product_name= %s, product_type=%s, product_description=%s WHERE product_id=%s AND user_id=%s', (name,type,description,product_id,user_id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('products'))
   
    return render_template('update_product.html', product=product)

#delete products route
@app.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM products WHERE product_id = %s AND user_id = %s', (product_id, user_id))
    product = cursor.fetchone()

    if product:
        cursor.execute('DELETE FROM products WHERE product_id = %s AND user_id = %s', (product_id, user_id))
        mysql.connection.commit()   
        cursor.close()
        flash('Product deleted successfully', 'success')        
    else:
        cursor.close()
        flash('Product not found or you do not have permission to delete it', 'danger')

    return redirect(url_for('products'))    

 
                                                                         # CUSTOMER PART


#customer route
@app.route('/customer')
def customer():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('customer.html')

#add customer route
@app.route('/add-customer')
def add_customer(): 
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    return render_template('add_customer.html')


                                                                          # BUSINESS PART

#businesses route   
@app.route('/businesses')
def businesses():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM business WHERE user_id = %s', (user_id,))
    businesses = cursor.fetchall()
    cursor.close()
    
    return render_template('businesses.html', businesses=businesses)

#add business route
@app.route('/add-business', methods=['GET', 'POST'])
def add_business(): 
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    
    user_id = session.get('user_id')

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        personname = request.form['personname']
        user_id = session.get('user_id')

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT  INTO business (business_name, business_address, phone_number, person_name, user_id) VALUES (%s, %s, %s, %s, %s)' , (name,address,phone,personname, user_id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('businesses'))


    return render_template('add_business.html')


#update buisness route
@app.route('/update-business/<int:business_id>', methods=['GET', 'POST'])
def update_business(business_id):
    if 'logged_in' not in session:
        return redirect (url_for('login'))
        
    
    user_id = session.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM business WHERE business_id = %s AND user_id = %s', (business_id, user_id))
    business = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']       
        phone = request.form['phone']
        personname = request.form['personname']


        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE business SET business_name = %s, business_address = %s, phone_number = %s, person_name = %s WHERE business_id = %s AND user_id = %s', 
                       (name, address, phone, personname, business_id, user_id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('businesses'))
    
    return render_template('update_business.html', business=business)


@app.route('/delete-business/<int:business_id>', methods=['POST'])
def delete_business(business_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')

    # Fetch the business details to check if it belongs to the logged-in user
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM business WHERE business_id = %s AND user_id = %s', (business_id, user_id))  
    business = cursor.fetchone()

    if business:
        # Delete the business
        cursor.execute('DELETE FROM business WHERE business_id = %s AND user_id = %s', (business_id, user_id))  
        mysql.connection.commit()  
        cursor.close()  
        flash('Business deleted successfully', 'success') 
    else:
        cursor.close()  
        flash('Business not found or you do not have permission to delete it', 'danger')  
    
    return redirect(url_for('businesses'))  
 


                                                                            # ORDERS PART




#orders route
@app.route('/orders')
def orders():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT order_id, business_name, customer_name, product_name, phone_number, quantity, status FROM orders WHERE user_id = %s',(user_id,))
    orders = cursor.fetchall()
    print(orders) 
    cursor.close()
    
    return render_template('orders.html', orders=orders)



#add orders route
@app.route('/add-orders', methods=['GET', 'POST'])
def add_orders():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')

    if request.method == 'POST':
        business_name = request.form['business']
        product_name = request.form['product']
        customer_name = request.form['customer']
        phone_number= request.form['phone_number']      
        quantity = request.form['quantity']
        status= request.form['status']

        # Initialize the cursor
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO orders (user_id,business_name,product_name,customer_name,phone_number,quantity,status) VALUES (%s,%s,%s,%s,%s,%s,%s)',(user_id, business_name,product_name, customer_name, phone_number, quantity, status))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('orders'))

    return render_template('add_orders.html')    



#update buisness route
@app.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
def update_order(order_id):
    if 'logged_in' not in session:
        return redirect (url_for('login'))
        
    
    user_id = session.get('user_id')

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM orders WHERE order_id = %s AND user_id = %s', (order_id, user_id))
    order = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        business = request.form['business']
        customer = request.form['customer']       
        product = request.form['product']
        phone_number = request.form['phone_number']
        quantity = request.form['quantity']
        status = request.form['status']


        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE orders SET business_name = %s, product_name = %s, customer_name = %s, phone_number = %s, quantity = %s,status = %s WHERE order_id = %s AND user_id = %s', 
                       (business,product, customer,  phone_number, quantity,status,order_id, user_id))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('orders'))
    
    return render_template('update_order.html', order=order)


#delete order route
@app.route('/delete-order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')

    # Fetch the business details to check if it belongs to the logged-in user
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM orders WHERE order_id = %s AND user_id = %s', (order_id, user_id))  
    order = cursor.fetchone()

    if order:
        # Delete the business
        cursor.execute('DELETE FROM orders WHERE order_id = %s AND user_id = %s', (order_id, user_id))  
        mysql.connection.commit()  
        cursor.close()  
        flash('Business deleted successfully', 'success')  
    else:
        cursor.close()  
        flash('Business not found or you do not have permission to delete it', 'danger')  
    
    return redirect(url_for('orders'))  

       
    

                                                                                                            # Profile 
   

#profile route
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    print(f"User ID from session: {session.get('user_id')}") 
    if 'logged_in' not in session:
        return redirect(url_for('login'))  

    user_id = session.get('user_id')  
    cursor = mysql.connection.cursor()  

    if request.method == 'POST':
        # Debugging form data
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        

        # Fetch the user's current password from the database
        cursor.execute('SELECT password FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()

       
        if user:
            print(f"Stored Password Hash: {user[0]}")
        else:
            print("No user found with this ID!")

        # Check if the current password matches the one in the database
        if not user or not check_password_hash(user[0], current_password):
            print("Current password doesn't match.")
            flash('Incorrect current password', 'danger')
        elif new_password != confirm_password:
            print("New passwords do not match.")
            flash('New passwords do not match', 'danger')
      
        else:
            # Hash the new password and update the database
            hashed_password = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed_password, user_id))
            mysql.connection.commit()

            # Check if the update was successful
            if cursor.rowcount > 0:
                print(f"Password updated for user_id: {user_id}")
                flash('Password updated successfully', 'success')
            else:
                print("No changes made to the database.")
                flash('No changes were made. Please try again.', 'danger')

        cursor.close()
        return redirect(url_for('profile'))

    # Fetch user information for the profile page
    cursor.execute('SELECT username, email FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()  

   
    if user_data:
        user_data_dict = {
            'username': user_data[0],  
            'email': user_data[1]      
        }
    else:
        user_data_dict = {}

    cursor.close()

    return render_template('profile.html', user=user_data_dict)





#currnet orders route
@app.route('/current-orders')
def current_orders():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    # Fetch all pending orders for the logged-in user
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT order_id, business_name, customer_name, product_name, phone_number, quantity, status FROM orders WHERE user_id = %s AND status = %s', (user_id, 'pending'))
    pending_orders = cursor.fetchall()
    cursor.close()

    return render_template('current_orders.html', pending_orders=pending_orders)


#update current status route
@app.route('/update-order-status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    # Get the new status from the form
    new_status = request.form['status']

    # Update the status of the order
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE orders SET status = %s WHERE order_id = %s AND user_id = %s', (new_status, order_id, user_id))
    mysql.connection.commit()
    cursor.close()

    flash('Order status updated successfully', 'success')
    return redirect(url_for('current_orders'))







   
#logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=False)