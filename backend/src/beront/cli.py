import click

from beront.shared.domain.errors import DomainError


def install_cli(app):
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
