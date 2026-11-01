from flask import Blueprint, current_app, g, request
from werkzeug.exceptions import UnsupportedMediaType

from beront.modules.identity.presentation.decorators import require_auth, require_permission
from beront.modules.media.presentation.schemas import MediaPatch, MediaQuery, MediaUpload
from beront.modules.media.presentation.serializers import asset_data
from beront.shared.domain.errors import DomainError
from beront.shared.presentation.schemas import VersionBody, json_body, query_body


def make_blueprint():
    bp = Blueprint("media_library", __name__, url_prefix="/api/v1/admin/media")

    @bp.get("")
    @require_auth
    @require_permission("catalog:read_private")
    def listing():
        params = query_body(MediaQuery)
        items, total = current_app.extensions["beront"].media.listing(**params)
        return {
            "data": [asset_data(a) for a in items],
            "meta": {"page": params["page"], "page_size": params["page_size"], "total": total},
        }

    @bp.post("")
    @require_auth
    @require_permission("catalog:write")
    def upload():
        if request.mimetype != "multipart/form-data":
            raise UnsupportedMediaType()
        if set(request.files) != {"file"} or len(request.files.getlist("file")) != 1:
            raise DomainError("VALIDATION_ERROR", "Adjunta una fotografía en el campo file.")
        fields = MediaUpload.model_validate(request.form.to_dict()).model_dump()
        asset, created = current_app.extensions["beront"].media.upload(
            request.files["file"].stream, fields["name"], g.admin.id, g.request_id
        )
        return {"data": asset_data(asset)}, 201 if created else 200

    @bp.patch("/<uuid:identifier>")
    @require_auth
    @require_permission("catalog:write")
    def update(identifier):
        asset = current_app.extensions["beront"].media.update(
            identifier, json_body(MediaPatch), g.admin.id, g.request_id
        )
        return {"data": asset_data(asset)}

    @bp.delete("/<uuid:identifier>")
    @require_auth
    @require_permission("catalog:write")
    def delete(identifier):
        current_app.extensions["beront"].media.delete(
            identifier, json_body(VersionBody)["version"], g.admin.id, g.request_id
        )
        return "", 204

    return bp
