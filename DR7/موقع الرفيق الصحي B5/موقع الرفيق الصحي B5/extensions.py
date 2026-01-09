from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# إنشاء instances بس لسه مش مربوطين بأي app
db = SQLAlchemy()
migrate = Migrate()
