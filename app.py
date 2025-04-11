import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from fpdf import FPDF
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
from models import db, User, Expense, Category, Budget

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Secure DB config
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(email=session['user']).first()
    expenses = Expense.query.filter_by(user_id=user.id).all()

    total = sum(e.amount for e in expenses)
    grouped = {}
    categories = set()
    category_totals = {}

    for e in expenses:
        y = e.date.year
        m = e.date.strftime('%B')
        grouped.setdefault(y, {}).setdefault(m, []).append(e)
        categories.add(e.category)
        category_totals[e.category] = category_totals.get(e.category, 0) + float(e.amount)

    return render_template("index.html", expenses=expenses, total=total,
                           grouped_expenses=grouped,
                           categories=sorted(categories),
                           category_data=category_totals)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("signup"))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user'] = user.email
            return redirect(url_for("index"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.")
    return redirect(url_for("login"))

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if user:
            flash(f"Reset link sent to {email} (mock)")
        else:
            flash("Email not found")
    return render_template("forgot_password.html")

@app.route("/add", methods=["POST"])
def add_expense():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(email=session['user']).first()
    expense = Expense(
        user_id=user.id,
        amount=request.form['amount'],
        category=request.form['category'],
        description=request.form['description'],
        date=datetime.strptime(request.form['date'], '%Y-%m-%d')
    )
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/filter", methods=["POST"])
def filter_view():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(email=session['user']).first()
    query = Expense.query.filter_by(user_id=user.id)

    category = request.form.get("category")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    if category:
        query = query.filter_by(category=category)
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)

    expenses = query.all()
    total = sum(e.amount for e in expenses)
    grouped = {}
    categories = set()
    category_totals = {}

    for e in expenses:
        y = e.date.year
        m = e.date.strftime('%B')
        grouped.setdefault(y, {}).setdefault(m, []).append(e)
        categories.add(e.category)
        category_totals[e.category] = category_totals.get(e.category, 0) + float(e.amount)

    return render_template("index.html", expenses=expenses, total=total,
                           grouped_expenses=grouped,
                           categories=sorted(categories),
                           category_data=category_totals)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(email=session['user']).first()

    if request.method == "POST":
        new_username = request.form['username']
        new_email = request.form['email']
        current_password = request.form['current_password']
        new_password = request.form.get('new_password')

        if not bcrypt.check_password_hash(user.password, current_password):
            flash("Current password is incorrect.")
            return redirect(url_for("profile"))

        user.username = new_username
        user.email = new_email

        if new_password:
            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        db.session.commit()
        session['user'] = user.email
        flash("Profile updated successfully!")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(email=session['user']).first()

    if request.method == 'POST':
        if 'category_name' in request.form:
            name = request.form['category_name']
            color = request.form.get('category_color') or '#007bff'
            if Category.query.filter_by(user_id=user.id, name=name).first():
                flash("Category already exists!")
            else:
                db.session.add(Category(name=name, color=color, user_id=user.id))
                db.session.commit()
                flash("Category added!")
            return redirect(url_for("manage"))

        elif 'budget_amount' in request.form:
            category_id = request.form['category_id']
            amount = request.form['budget_amount']
            month = request.form['month']
            db.session.add(Budget(user_id=user.id, category_id=category_id, amount=amount, month=month))
            db.session.commit()
            flash("Budget added!")
            return redirect(url_for("manage"))

    categories = Category.query.filter_by(user_id=user.id).all()
    budgets = Budget.query.join(Category).filter(Budget.user_id == user.id).add_columns(
        Budget.id, Budget.amount, Budget.month, Category.name.label("category_name"), Category.color
    ).order_by(Budget.month.desc()).all()

    usage = {}
    for b in budgets:
        spent = db.session.query(db.func.sum(Expense.amount)).filter(
            Expense.user_id == user.id,
            Expense.category == b.category_name,
            db.func.date_format(Expense.date, '%Y-%m') == b.month
        ).scalar() or 0
        usage[b.id] = float(spent)

    return render_template("manage.html", categories=categories, budgets=budgets, usage=usage)

@app.route("/delete-category/<int:id>")
def delete_category(id):
    if "user" not in session:
        return redirect(url_for("login"))
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted")
    return redirect(url_for("manage"))

@app.route("/delete-budget/<int:id>")
def delete_budget(id):
    if "user" not in session:
        return redirect(url_for("login"))
    budget = Budget.query.get_or_404(id)
    db.session.delete(budget)
    db.session.commit()
    flash("Budget deleted")
    return redirect(url_for("manage"))

@app.route("/export/excel")
def export_excel():
    if "user" not in session:
        return redirect(url_for("login"))
    user = User.query.filter_by(email=session['user']).first()
    expenses = Expense.query.filter_by(user_id=user.id).all()
    df = pd.DataFrame([e.__dict__ for e in expenses])
    df.drop(columns=['_sa_instance_state'], inplace=True)
    filepath = "data/expenses_export.xlsx"
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)

@app.route("/export/pdf")
def export_pdf():
    if "user" not in session:
        return redirect(url_for("login"))
    user = User.query.filter_by(email=session['user']).first()
    expenses = Expense.query.filter_by(user_id=user.id).all()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Expense Report", ln=True, align="C")
    for e in expenses:
        line = f"{e.date} | ${e.amount} | {e.category} | {e.description}"
        pdf.cell(200, 10, txt=line, ln=True)
    filepath = "data/expenses_export.pdf"
    pdf.output(filepath)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
