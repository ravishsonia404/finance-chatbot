from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# USER MODEL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# CREATE DB
with app.app_context():
    db.create_all()

# HOME
@app.route('/')
def home():
    if 'user' in session:
        return render_template("index.html")
    return redirect('/login')

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "⚠️ User already exists"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template("register.html")

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user'] = user.username
            return redirect('/')
        else:
            return "❌ Invalid credentials"

    return render_template("login.html")

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ANALYZE CSV
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user' not in session:
        return redirect('/login')

    file = request.files.get('file')

    if not file:
        return "⚠️ No file uploaded"

    df = pd.read_csv(file)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    if 'revenue' not in df.columns or 'expenses' not in df.columns:
        return "❌ CSV must contain 'Revenue' and 'Expenses' columns"

    revenue = df['revenue'].sum()
    expenses = df['expenses'].sum()
    profit = revenue - expenses

    if profit > 0:
        insight = "✅ Your business is in profit"
    else:
        insight = "⚠️ Your business is in loss"

    return render_template("index.html",
                           revenue=revenue,
                           expenses=expenses,
                           profit=profit,
                           insight=insight)

if __name__ == '__main__':
    app.run(debug=True)