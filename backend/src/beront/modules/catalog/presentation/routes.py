from flask import Blueprint, current_app, g, request, send_file, session
from werkzeug.exceptions import UnsupportedMediaType

from beront.modules.catalog.presentation.schemas import (
    BrandCreate,
    BrandPatch,
    CatalogQuery,
    DefinitionCreate,
    DefinitionPatch,
    ImageAttach,
    ImageCreate,
    ImagePatch,
    LocaleQuery,
    PresentationCreate,
    ProductCreate,
    ProductPatch,
    VariantCreate,
    VariantPatch,
)
from beront.modules.catalog.presentation.serializers import (
    brand_data,
    image_data,
    product_data,
    variant_data,
)
from beront.modules.identity.domain.policies import PERMISSIONS
from beront.modules.identity.presentation.decorators import require_auth, require_permission
from beront.shared.domain.errors import DomainError, Unauthorized
from beront.shared.presentation.schemas import VersionBody, json_body, query_body

REPEATABLE = (
    "kind",
    "brand_id",
    "classification",
    "audience",
    "accord",
    "usage",
    "profile",
    "volume_ml",
)


def services():
    return current_app.extensions["beront"]


def make_blueprint():
    bp = Blueprint("catalog", __name__)

    @bp.get("/api/v1/catalog/products")
    def public_products():
        filters = query_body(CatalogQuery, REPEATABLE)
        views, total = services().queries.search(filters)
        return {
            "data": [product_data(v.product, view=v, locale=filters["locale"]) for v in views],
            "meta": {"page": filters["page"], "page_size": filters["page_size"], "total": total},
        }

    @bp.get("/api/v1/catalog/products/<slug>")
    def public_detail(slug):
        locale = query_body(LocaleQuery)["locale"]
        view = services().queries.detail(slug)
        return {"data": product_data(view.product, view=view, locale=locale)}

    @bp.get("/api/v1/catalog/facets")
    def facets():
        query_body(LocaleQuery)
        return {"data": services().queries.facets()}

    @bp.get("/api/v1/admin/products")
    @require_auth
    @require_permission("catalog:read_private")
    def private_products():
        filters = query_body(CatalogQuery, REPEATABLE)
        views, total = services().queries.search(filters, private=True)
        return {
            "data": [
                product_data(v.product, private=True, view=v, locale=filters["locale"])
                for v in views
            ],
            "meta": {"page": filters["page"], "page_size": filters["page_size"], "total": total},
        }

    @bp.get("/api/v1/admin/products/<uuid:identifier>")
    @require_auth
    @require_permission("catalog:read_private")
    def private_detail(identifier):
        return {"data": product_data(services().catalog.product(identifier), private=True)}

    @bp.post("/api/v1/admin/products")
    @require_auth
    @require_permission("catalog:write")
    def create_product():
        product = services().catalog.create_product(
            json_body(ProductCreate), g.admin.id, g.request_id
        )
        return {"data": product_data(product, private=True)}, 201

    @bp.patch("/api/v1/admin/products/<uuid:identifier>")
    @require_auth
    @require_permission("catalog:write")
    def update_product(identifier):
        product = services().catalog.update_product(
            identifier, json_body(ProductPatch), g.admin.id, g.request_id
        )
        return {"data": product_data(product, private=True)}

    @bp.post("/api/v1/admin/products/<uuid:identifier>/variants")
    @require_auth
    @require_permission("catalog:write")
    def create_variant(identifier):
        result = services().catalog.create_variant(
            identifier, json_body(VariantCreate), g.admin.id, g.request_id
        )
        return {"data": variant_data(result, private=True)}, 201

    @bp.patch("/api/v1/admin/variants/<uuid:identifier>")
    @require_auth
    @require_permission("catalog:write")
    def update_variant(identifier):
        result = services().catalog.update_variant(
            identifier, json_body(VariantPatch), g.admin.id, g.request_id
        )
        return {"data": variant_data(result, private=True)}

    @bp.get("/api/v1/admin/brands")
    @require_auth
    @require_permission("catalog:read_private")
    def brands():
        return {"data": [brand_data(b) for b in services().catalog.brands(private=True)]}

    @bp.get("/api/v1/admin/catalog-options/<resource>")
    @require_auth
    @require_permission("catalog:read_private")
    def definitions(resource):
        return {"data": services().catalog.definitions(resource, private=True)}

    @bp.post("/api/v1/admin/catalog-options/<resource>")
    @require_auth
    @require_permission("catalog:write")
    def create_definition(resource):
        schema = PresentationCreate if resource == "presentations" else DefinitionCreate
        data = json_body(schema)
        return {
            "data": services().catalog.create_definition(resource, data, g.admin.id, g.request_id)
        }, 201

    @bp.patch("/api/v1/admin/catalog-options/<resource>/<uuid:identifier>")
    @require_auth
    @require_permission("catalog:write")
    def update_definition(resource, identifier):
        return {
            "data": services().catalog.update_definition(
                resource, identifier, json_body(DefinitionPatch), g.admin.id, g.request_id
            )
        }

    @bp.post("/api/v1/admin/brands")
    @require_auth
    @require_permission("catalog:write")
    def create_brand():
        return {
            "data": brand_data(
                services().catalog.create_brand(json_body(BrandCreate), g.admin.id, g.request_id)
            )
        }, 201

    @bp.patch("/api/v1/admin/brands/<uuid:identifier>")
    @require_auth
    @require_permission("catalog:write")
    def update_brand(identifier):
        return {
            "data": brand_data(
                services().catalog.update_brand(
                    identifier, json_body(BrandPatch), g.admin.id, g.request_id
                )
            )
        }

    @bp.post("/api/v1/admin/products/<uuid:identifier>/images")
    @require_auth
    @require_permission("catalog:write")
    def create_image(identifier):
        if request.is_json:
            fields = json_body(ImageAttach)
            asset_id = fields.pop("asset_id")
            image = services().catalog.attach_image(
                identifier, asset_id, fields, g.admin.id, g.request_id
            )
            return {"data": image_data(image, private=True)}, 201
        if request.mimetype != "multipart/form-data":
            raise UnsupportedMediaType()
        if set(request.files) != {"file"} or len(request.files.getlist("file")) != 1:
            raise DomainError("VALIDATION_ERROR", "Adjunta una sola fotografía en el campo file.")
        fields = ImageCreate.model_validate(request.form.to_dict()).model_dump()
        image = services().catalog.add_image(
            identifier, request.files["file"].stream, fields, g.admin.id, g.request_id
        )
        return {"data": image_data(image, private=True)}, 201

    @bp.patch("/api/v1/admin/images/<uuid:identifier>")
    @require_auth
    @require_permission("catalog:write")
    def update_image(identifier):
        image = services().catalog.update_image(
            identifier, json_body(ImagePatch), g.admin.id, g.request_id
        )
        return {"data": image_data(image, private=True)}

    @bp.delete("/api/v1/admin/images/<uuid:identifier>")
    @require_auth
    @require_permission("catalog:write")
    def delete_image(identifier):
        data = json_body(VersionBody)
        services().catalog.delete_image(identifier, data["version"], g.admin.id, g.request_id)
        return "", 204

    @bp.get("/media/<filename>")
    def media(filename):
        path = services().storage.path(filename)
        private = False
        if session.get("sid"):
            try:
                services().identity.authenticate(session["sid"])
                private = "catalog:read_private" in PERMISSIONS
            except Unauthorized:
                session.clear()
        services().media.visible(filename, private=private)
        if not path.is_file():
            from beront.shared.domain.errors import NotFound

            raise NotFound()
        response = send_file(path, mimetype="image/webp", conditional=True)
        response.headers["Cache-Control"] = "private, no-store"
        return response

    return bp
