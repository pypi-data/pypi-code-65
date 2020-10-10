import click


# from .visualsim import *

def duck_art():
    duck = """
            ,----,
       ___.`      `,
       `===  D     :
         `'.      .'
            )    (                   ,
           /      \_________________/|
          /                          |
         |                           ;
         |               _____       /
         |      \       ______7    ,'
         |       \    ______7     /
          \       `-,____7      ,'   jgs
    ^~^~^~^`\                  /~^~^~^~^
      ~^~^~^ `----------------' ~^~^~^
     ~^~^~^~^~^^~^~^~^~^~^~^~^~^~^~^~
    """
    return duck


@click.command()
@click.option('--verbose', is_flag=True, help="Will print verbose messages.")
@click.option('--name', default='', help='Who are you?')
# @click.option('--visualsim', is_flag=False, help='CEG 4136 Lab Launcher Tool')
def cli(verbose, name):
    click.echo(duck_art())
    click.echo("Hello World. Welcome to PyNevin CLI")
    if verbose:
        click.echo("We are in the verbose mode.")
    # if visualsim_bool:
    # run()
    click.echo('Bye {0}'.format(name))
