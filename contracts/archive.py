import click

@click.command()
@click.option('--fr', default=None, help="The tools/service to go from.")
@click.option('--to', default=None, help="The tools/service to go to.")
@click.option('--rs', default=None, help="The recordstore to transform from.")
@click.option('--op', default=None, help="The path to put the generated recordstore.")

def main(fr, to, rs, op):
    print("To be done.")