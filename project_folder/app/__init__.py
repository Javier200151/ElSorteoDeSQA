from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'tu_clave_secreta'

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
