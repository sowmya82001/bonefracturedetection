from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
import random
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change to your actual secret key
DATABASE = os.path.join('instance', 'users.db')

# Ensure 'instance' directory exists
os.makedirs('instance', exist_ok=True)

# Initialize users table if not exists
def init_users_table():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        conn.commit()

# Initialize doctors table
@app.route('/init_db')
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bone_experts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            mobile TEXT,
            address TEXT,
            hospital TEXT,
            qualification TEXT,
            specialization TEXT
        )
        ''')
        conn.commit()
    init_users_table()
    return "Databases initialized successfully!"

# Homepage
@app.route('/')
def home():
    return render_template("index.html")

# Predict
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename != '':
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            diseases = ["Metacarpal","Melanoma","Fabula","Eczema"]
            result = random.choice(diseases)
            confidence = round(random.uniform(0.75, 0.99), 4)

            return render_template('predict.html', result=result, confidence=confidence, image_path=filepath)

        return render_template('predict.html', error="No file selected.")
    
    return render_template('predict.html')

# View Doctors
@app.route('/dr_fetch')
def dr_fetch():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bone_experts')
    doctors = cursor.fetchall()
    conn.close()
    return render_template('dr_fetch.html', doctors=doctors)

# Add Doctor
@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['email'],
            request.form['password'],
            request.form['mobile'],
            request.form['address'],
            request.form['hospital'],
            request.form['qualification'],
            request.form['specialization']
        )

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO bone_experts 
            (name, email, password, mobile, address, hospital, qualification, specialization)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        conn.close()

        flash("Doctor added successfully!", "success")
        return redirect(url_for('dr_fetch'))

    return render_template('add_doctor.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            user = cur.fetchone()
            if user:
                session['user'] = user[1]  # name
                flash("Login Successful", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid Credentials", "danger")
    return render_template('login.html')

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        try:
            with sqlite3.connect(DATABASE) as conn:
                conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                conn.commit()
                flash("Registration successful! Please login.", "success")
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "danger")
    return render_template('signup.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('home'))

# Main
if __name__ == '__main__':
    init_users_table()
    app.run(debug=True)
