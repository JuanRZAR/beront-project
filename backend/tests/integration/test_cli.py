def test_cli_exposes_short_management_commands(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["importar-catalogo", "--solo-validar"])
    assert result.exit_code == 0, result.output
    assert "Semilla válida: 130 perfumes" in result.output
    for command in ("migrate", "createsuperuser", "reset-password"):
        assert command in app.cli.commands


def test_import_catalog_requires_administrator(app):
    result = app.test_cli_runner().invoke(args=["importar-catalogo"])
    assert result.exit_code != 0
    assert "createsuperuser" in result.output
