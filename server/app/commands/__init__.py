import click


@click.group()
def cli():
    pass


from .cameras import cameras as cameras_commands


cli.add_command(cameras_commands, 'cameras')
