import importlib.util
from pathlib import Path

import click

from beront.shared.domain.errors import DomainError

BACKEND = Path(__file__).resolve().parents[2]


def main():
    from flask.cli import FlaskGroup

    from beront.app import create_app

    FlaskGroup(create_app=create_app, help="Administración de BÉRONT.").main(prog_name="beront")


def load_seed_module():
    spec = importlib.util.spec_from_file_location(
        "importar_catalogo", BACKEND / "semillas" / "importar_catalogo.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_cli(app):
    @app.cli.command("inicializar-home")
    def initialize_home():
        """Instala los mensajes aprobados sin sobrescribir los ya editados."""
        from beront.modules.commerce.application.seed_home import SeedHomeMessages

        try:
            count = SeedHomeMessages(app.extensions["beront"].uow_factory).execute()
        except DomainError as error:
            raise click.ClickException(str(error)) from error
        click.echo(f"Home: {count} mensajes creados; los existentes se conservan.")

    @app.cli.command("createsuperuser")
    @click.option("--username", prompt="Usuario")
    @click.password_option(confirmation_prompt=True)
    def createsuperuser(username, password):
        try:
            app.extensions["beront"].identity.create_admin(username, password)
        except (ValueError, DomainError) as error:
            raise click.ClickException(str(error)) from error
        click.echo("Administrador único creado.")

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.password_option(confirmation_prompt=True)
    def create_admin(username, password):
        try:
            app.extensions["beront"].identity.create_admin(username, password)
        except (ValueError, DomainError) as error:
            raise click.ClickException(str(error)) from error
        click.echo("Administrador creado.")

    @app.cli.command("reset-password")
    @click.argument("username")
    @click.password_option(confirmation_prompt=True)
    def reset_password(username, password):
        try:
            app.extensions["beront"].identity.reset_password(username, password)
        except (ValueError, DomainError) as error:
            raise click.ClickException(str(error)) from error
        click.echo("Contraseña actualizada y sesiones revocadas.")

    @app.cli.command("migrate")
    def migrate():
        """Aplica las migraciones pendientes (alembic upgrade head)."""
        from alembic import command
        from alembic.config import Config

        command.upgrade(Config(str(BACKEND / "alembic.ini")), "head")
        click.echo("Base de datos al día.")

    @app.cli.command("importar-catalogo")
    @click.option("--solo-validar", is_flag=True, help="Valida la semilla sin escribir en la base.")
    def import_catalog(solo_validar):
        """Importa perfumes, fotografías y configuración inicial desde backend/semillas."""
        seed = load_seed_module()
        document = seed.load_source()
        click.echo(
            f"Semilla válida: {len(document['products'])} perfumes y "
            f"{len(document['images'])} imágenes."
        )
        if solo_validar:
            return
        try:
            seed.import_into(app, document)
        except (ValueError, DomainError) as error:
            raise click.ClickException(str(error)) from error

    @app.cli.command("importar-recortes")
    @click.option(
        "--manifiesto", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path)
    )
    @click.option(
        "--solo-validar", is_flag=True, help="Valida archivos y vínculos sin modificarlos."
    )
    def import_photos(manifiesto, solo_validar):
        """Aplica los PNG aprobados de Inkscape al catálogo importado."""
        from beront.modules.catalog.application.import_photos import ImportCatalogPhotos
        from beront.modules.catalog.infrastructure.approved_images import load_approved_images

        try:
            seed = load_seed_module()
            replacements, open_image = load_approved_images(
                manifiesto, seed.load_source(), seed.SOURCE / "imagenes"
            )
            services = app.extensions["beront"]
            result = ImportCatalogPhotos(services.uow_factory, services.storage).execute(
                replacements, open_image, dry_run=solo_validar
            )
        except (OSError, ValueError, KeyError, DomainError) as error:
            raise click.ClickException(str(error)) from error
        prefix = "Validación" if solo_validar else "Importación"
        click.echo(
            f"{prefix}: {result['images']} recortes, {result['products']} perfumes, "
            f"{result['replaced']} vínculos y {result['skipped']} ya aplicados."
        )
