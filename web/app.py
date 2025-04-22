from flask import Flask, render_template, request
from models import PasswordEntry
from db import db
from password_generator import generate_password
import os
import time
import sqlalchemy.exc

# Initialize Flask app
app = Flask(__name__)

# DB connection settings
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql://postgres:postgres@db:5432/password_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Bind SQLAlchemy to Flask app
db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    password = ""
    if request.method == 'POST':
        length = int(request.form.get('length', 12))
        use_upper = bool(request.form.get('uppercase'))
        use_lower = bool(request.form.get('lowercase'))
        use_digits = bool(request.form.get('digits'))
        use_symbols = bool(request.form.get('symbols'))

        password = generate_password(length, use_upper, use_lower, use_digits, use_symbols)
        new_entry = PasswordEntry(password=password)
        db.session.add(new_entry)
        db.session.commit()

    return render_template('index.html', password=password)

# Retry DB connection and table creation
if __name__ == '__main__':
    with app.app_context():
        for i in range(10):
            try:
                db.create_all()
                print("✅ Database is ready. Tables created.")
                break
            except sqlalchemy.exc.OperationalError:
                print(f"⏳ Attempt {i+1}/10: Waiting for the database to be ready...")
                time.sleep(3)
        else:
            print("❌ Could not connect to the database after several attempts.")
            exit(1)

    app.run(debug=True, host='0.0.0.0')
