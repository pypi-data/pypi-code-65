import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
try:
    from rich import print
except ImportError as e:
    print(repr(e))
from ciphit.basemods.Ciphers import aes


def print_help():
    ctx = click.get_current_context()
    click.echo(ctx.get_help())

@click.command()
@optgroup.group(
        "Mutually Exclusive", 
        cls=RequiredMutuallyExclusiveOptionGroup,
)
@optgroup.option(
        "-e", "--encode", 
        default=False, 
        type=str,
)
@optgroup.option(
        "-d", "--decode", 
        default=False, 
        type=str,
)
@click.option(
        "-k", "--key", 
        prompt=True, 
        hide_input=True, 
        confirmation_prompt=True,
)
def main(**kwargs):
    cpt = aes.Crypt()
    encode, decode, key = \
    kwargs['encode'], kwargs['decode'], kwargs['key']
    if encode:
        _ = cpt.Encode(encode,key)
        print(f"[bold yellow]{_}[/bold yellow]")
    elif decode:
        _ = cpt.Decode(decode,key)
        print(f"[bold green]{_}[/bold green]")
    else:
        print_help()
        exit(-1)

if __name__ == '__main__':
    main()
