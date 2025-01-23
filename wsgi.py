import os
from app import create_app, db
from app.config import Config
from flask_migrate import Migrate

app = create_app(Config)
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 