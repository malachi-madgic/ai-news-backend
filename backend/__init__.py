from flask import Flask

from backend.app.api.daily_digest import daily_digest_bp

app = Flask(__name__)

app.register_blueprint(daily_digest_bp)

# Additional app configuration and routes can be added here
