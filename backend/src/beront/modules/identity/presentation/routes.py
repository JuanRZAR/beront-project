from flask import Blueprint, current_app, g, session
from flask_wtf.csrf import generate_csrf

from beront.modules.identity.presentation.decorators import require_auth
from beront.modules.identity.presentation.schemas import LoginBody
from beront.modules.identity.presentation.serializers import administrator_data
from beront.shared.presentation.schemas import json_body


def make_blueprint(limiter):
    bp = Blueprint("identity", __name__, url_prefix="/api/v1/auth")

    @bp.get("/csrf")
    def csrf_token():
        return {"data": {"csrf_token": generate_csrf()}}

    @bp.post("/login")
    @limiter.limit("5 per 15 minutes")
    def login():
        data = json_body(LoginBody)
        service = current_app.extensions["beront"].identity
        old_token = session.get("sid")
        admin, token = service.login(**data, request_id=g.request_id)
        if old_token:
            service.logout(old_token, g.request_id)
        session.clear()
        session["sid"] = token
        session.permanent = True
        result = administrator_data(admin)
        result["csrf_token"] = generate_csrf()
        return {"data": result}

    @bp.get("/session")
    @require_auth
    def read_session():
        return {"data": administrator_data(g.admin)}

    @bp.post("/logout")
    @require_auth
    def logout():
        current_app.extensions["beront"].identity.logout(session["sid"], g.request_id)
        session.clear()
        return "", 204

    return bp
