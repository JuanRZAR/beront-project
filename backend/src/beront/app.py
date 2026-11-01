from datetime import timedelta

from flask import Flask
from flask_limiter import Limiter
from flask_wtf.csrf import CSRFProtect

from beront.bootstrap import build_container
from beront.cli import install_cli
from beront.config import Settings
from beront.modules.cart.presentation.routes import make_blueprint as cart_blueprint
from beront.modules.catalog.presentation.routes import make_blueprint as catalog_blueprint
from beront.modules.commerce.presentation.routes import make_blueprint as commerce_blueprint
from beront.modules.identity.presentation.routes import make_blueprint as identity_blueprint
from beront.modules.inventory.presentation.routes import make_blueprint as inventory_blueprint
from beront.modules.media.presentation.routes import make_blueprint as media_blueprint
from beront.modules.orders.presentation.routes import make_blueprint as orders_blueprint
from beront.shared.infrastructure.logging import configure_logging
from beront.shared.presentation.errors import install_errors
from beront.shared.presentation.security import client_address, install_security


def create_app(settings=None, mailer=None):
    settings = settings or Settings.from_env()
    app = Flask(__name__, static_folder=None)
    app.config.update(
        SECRET_KEY=settings.secret_key,
        TESTING=settings.testing,
        DEBUG=False,
        MAX_CONTENT_LENGTH=65536,
        MAX_FORM_MEMORY_SIZE=65536,
        MAX_FORM_PARTS=8,
        SESSION_COOKIE_NAME="beront_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_PATH="/",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        SESSION_REFRESH_EACH_REQUEST=False,
        TRUSTED_HOSTS=["localhost", "127.0.0.1", "[::1]"],
        WTF_CSRF_TIME_LIMIT=3600,
        RATELIMIT_ENABLED=settings.rate_limits,
        RATELIMIT_HEADERS_ENABLED=True,
    )
    configure_logging(settings.storage_root / "logs", testing=settings.testing)
    app.extensions["beront"] = build_container(settings, mailer)
    install_errors(app)
    install_security(app, settings)
    csrf = CSRFProtect(app)
    limiter = Limiter(
        client_address, app=app, default_limits=["300 per minute"], storage_uri="memory://"
    )
    app.extensions["beront_limiter"] = limiter
    app.register_blueprint(identity_blueprint(limiter))
    app.register_blueprint(catalog_blueprint())
    app.register_blueprint(inventory_blueprint())
    app.register_blueprint(media_blueprint())
    app.register_blueprint(commerce_blueprint())
    app.register_blueprint(orders_blueprint(csrf, limiter))
    app.register_blueprint(cart_blueprint(csrf, limiter))
    install_cli(app)
    return app
