import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///campus_events.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# initialize the app with the extension
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models and routes
    import models
    import routes
    
    # Create all tables
    db.create_all()
    
    # Create default admin user if none exists
    from models import College, User
    from werkzeug.security import generate_password_hash
    
    if not College.query.first():
        # Create a default college
        default_college = College(
            name="Demo University",
            code="DEMO",
            address="123 Campus Street, Education City"
        )
        db.session.add(default_college)
        db.session.commit()
        
        # Create default admin user
        admin_user = User(
            username="admin",
            email="admin@demo.edu",
            password_hash=generate_password_hash("admin123"),
            full_name="System Administrator",
            role="admin",
            college_id=default_college.id
        )
        db.session.add(admin_user)
        db.session.commit()
        
        logging.info("Created default college and admin user (admin/admin123)")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
