import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "src" / "beront"


def test_domain_is_framework_free():
    for path in ROOT.rglob("domain/*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            imports = []
            if isinstance(node, ast.Import):
                imports = [item.name for item in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports = [node.module]
            for name in imports:
                assert name.split(".")[0] not in {"flask", "sqlalchemy", "pydantic", "werkzeug"}
                if name.startswith("beront."):
                    assert ".domain." in name


def test_http_layer_does_not_import_orm():
    for path in ROOT.rglob("presentation/*.py"):
        contents = path.read_text(encoding="utf-8")
        assert "sqlalchemy" not in contents or path.name == "errors.py"
        assert ".infrastructure.models" not in contents
        assert ".infrastructure.repositories" not in contents


def test_all_administrative_endpoints_are_guarded(app):
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith("/api/v1/admin/"):
            view = app.view_functions[rule.endpoint]
            assert view.requires_auth
            assert view.required_permission


def test_no_runtime_ddl():
    for path in ROOT.rglob("*.py"):
        assert ".create_all(" not in path.read_text(encoding="utf-8")
