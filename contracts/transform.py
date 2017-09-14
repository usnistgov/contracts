import click

@click.command()
@click.option('--fr', default=None, help="The tools/service to go from.")
@click.option('--to', default=None, help="The tools/service to go to.")
@click.option('--sc', default=None, help="The schema to transform from.")
@click.option('--op', default=None, help="The path to put the transformed schema.")

def main(fr, to, sc, op):
    print("To be done.")