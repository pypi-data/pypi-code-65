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
        is_flag=True,
        flag_value=True,
)
@optgroup.option(
        "-d", "--decode",
        is_flag=True,
        flag_value=True,
)
@click.option(
        "-t", "--text",
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

    text = kwargs['text']
    if not text:
        print("[blue]Opening editor[/blue]")
        click.pause()
        text=click.edit(text='')
        if text in (None,''):
            print("[bold red]error:[/bold red] empty text")
            exit(-1)
        text=text.strip('\n')

    cpt = aes.Crypt()
    encode, decode, key= \
    kwargs['encode'], kwargs['decode'], kwargs['key']
    if encode:
        _ = cpt.Encode(text,key)
        print(f"[bold yellow]{_}[/bold yellow]")
    elif decode:
        _ = cpt.Decode(text,key)
        print(f"[bold green]{_}[/bold green]")
    else:
        print_help()
        exit(-1)

if __name__ == '__main__':
    main()
