from flask import Flask
from .api.articles import articles_bp
from .api.daily_digest import daily_digest_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(articles_bp, url_prefix='/articles')
    app.register_blueprint(daily_digest_bp, url_prefix='/digest')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
