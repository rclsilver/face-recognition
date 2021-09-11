import click


@click.group()
def cli():
    pass


from .cameras import cameras as cameras_commands


cli.add_command(cameras_commands, 'cameras')


@cli.command()
def test():
    from app.database import SessionLocal
    from app.controllers.recognition import RecognitionController

    db = SessionLocal()

    RecognitionController.compute_suggestions(db)

    db.close()
