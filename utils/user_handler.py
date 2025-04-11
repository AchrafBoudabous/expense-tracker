import json
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def load_users(filepath):
    try:
        with open(filepath, "r") as f:
            data = f.read().strip()
            return json.loads(data) if data else []
    except FileNotFoundError:
        return []

def save_user(filepath, user):
    users = load_users(filepath)
    users.append(user)
    with open(filepath, "w") as f:
        json.dump(users, f, indent=4)

def get_user_by_email(filepath, email):
    users = load_users(filepath)
    for user in users:
        if user["email"] == email:
            return user
    return None

def authenticate_user(filepath, email, password):
    user = get_user_by_email(filepath, email)
    if user and check_password(user["password"], password):
        return user
    return None

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(hashed, password):
    return bcrypt.check_password_hash(hashed, password)