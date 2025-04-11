# 💰 Expense Tracker Web App

A simple and modern expense tracking web application built with **Flask**, **MySQL**, and **SQLAlchemy**, designed for personal budgeting, category management, and visual insights.

## ✨ Features

- 🔐 User Authentication (Signup/Login/Password Update)
- 💸 Add & filter expenses with date/category
- 📁 Category Management (create/delete)
- 💰 Budget per category per month
- 📊 Budget usage visualized with progress bars
- 📈 Pie chart of expenses by category
- 🔄 Export to Excel & PDF
- 🌃 Dark/light mode toggle with system preference
- 🔐 Secrets and DB credentials stored via `.env` file
- ⚙️ Modern Bootstrap UI with mobile responsiveness

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker
```

### 2. Set Up a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.template .env
```

Update your `.env` file with your MySQL credentials:

```env
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
DB_NAME=expense_tracker
SECRET_KEY=your-super-secret-key
```

### 5. Set Up the MySQL Database

Create the database manually or via terminal:

```sql
CREATE DATABASE expense_tracker;
```

Then, in Python shell or using Flask CLI:

```python
from models import db
from app import app

with app.app_context():
    db.create_all()
```

---

## 🥪 Run the App

```bash
python app.py
```

Visit `http://127.0.0.1:5000/` in your browser.

---

## 📁 Project Structure

```
expense-tracker/
|
├── app.py                # Main Flask application
├── models.py             # SQLAlchemy models
├── templates/            # HTML templates (Jinja2)
├── static/               # CSS, JS, assets
├── .env                  # Environment variables (not tracked in Git)
├── .env.template         # Template for env vars
├── requirements.txt      # Python dependencies
└── README.md             # You're reading it!
```

---

## ✅ To-Do / Future Features

- 📱 Mobile-first UI improvements
- 📅 Recurring expenses
- 📈 Monthly comparison dashboard
- 🔔 Notifications on budget thresholds
- 🣟 Receipt uploads

---

## 🤝 Contributing

1. Fork the repo
2. Create a new branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License. Use freely, modify, and improve!

---

## 🙌 Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Bootstrap](https://getbootstrap.com/)
- [Chart.js](https://www.chartjs.org/)
- [FPDF](https://pyfpdf.readthedocs.io/)

---

