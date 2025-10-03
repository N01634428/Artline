from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

users=[
    { 'username' : 'Jacky', 'email': 'hello12@gmail.com', 'password' : '12345' }
]

@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = None 
        for u in users:
            if u['email'] == email and u['password'] == password:
                user=u
                break


        if user: 
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid Username or Password. Please try again.' , 
        
    return render_template('login.html')    


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        con_pas = request.form['confirm-password']

        if password != con_pas:
            return 'Password and confirm password do not match'
        

        if any(u['email'] == email for u in users):
            return 'This email is already registerd'
        
        users.append({'username': username , 'email' : email , 'password': password})
        return redirect(url_for('login'))
    
    return render_template('signup.html')



@app.route('/dashboard')
def dashboard():
    return 'Welcome Jacky'



if __name__ == '__main__':
    app.run(debug=True)
