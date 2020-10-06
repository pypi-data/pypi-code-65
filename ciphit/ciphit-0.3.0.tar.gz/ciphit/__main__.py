import click
from click_option_group import (
    optgroup, 
    MutuallyExclusiveOptionGroup,
    RequiredMutuallyExclusiveOptionGroup,
)
from rich import print
from ciphit.basemods.Ciphers import aes

def get_singleline(multi: list) -> repr:
    return repr('\n'.join([i.strip('\n') for i in multi]))

def get_multiline(single: str) -> str:
    return '\n'.join(single.strip("'").split("\\n"))

def print_help():
    ctx = click.get_current_context()
    click.echo(ctx.get_help())

@click.command()
@optgroup.group(
        "Encode/Decode", 
        cls=RequiredMutuallyExclusiveOptionGroup,
)
@optgroup.option(
        "-e", "--encode", is_flag=True, flag_value=True,
)
@optgroup.option(
        "-d", "--decode", is_flag=True, flag_value=True,
)
@click.option(
        "-k","--key", 
        help="The key with which text is Encoded/Decoded.", 
        prompt=True, 
        hide_input=True, 
        confirmation_prompt=True,
)
@optgroup.group(
        "Text/File", 
        cls=MutuallyExclusiveOptionGroup,
)
@optgroup.option(
    "-t", "--text",
    help="The text you want to Encode/Decode.", 
    default=False, type=str,
)
@optgroup.option(
    "-f", "--file", 
    type=click.File('r+'), 
    default=None,
)
def main(**kwargs):

    isFile = not kwargs['file'] is None
    if not kwargs['text'] and not isFile:
        print("[bold blue]Opening editor[/bold blue]")
        click.pause()
        kwargs['text']=click.edit(text='')
        if kwargs['text'] in (None,''):
            print("[bold red]error:[/bold red] Text is empty.")
            exit(-1)
        kwargs['text']=kwargs['text'].strip('\n')

    cpt = aes.Crypt()
    if not isFile:
        if kwargs['encode']:
            _ = cpt.Encode(kwargs['text'],kwargs['key'])
            print(f"Final result: [bold yellow]{_}[/bold yellow]")
        else:#kwargs['decode']
            _ = cpt.Decode(kwargs['text'],kwargs['key'])
            print(f"Final result: [bold green]{_}[/bold green]")
    elif isFile:
        if kwargs['encode']:
            _ = cpt.Encode(get_singleline(kwargs['file'].readlines()), kwargs['key'])
            msg="[bold orange]File is now enncrypted.[/bold orange]"
        else:#kwargs['decode']
            _ = get_multiline(cpt.Decode(kwargs['file'].read().strip(), kwargs['key']))
            msg="[bold green]File is now decrypted.[/bold green]"
        kwargs['file'].truncate(0)
        kwargs['file'].seek(0)
        kwargs['file'].write(_)
        print(msg)
    else:
        #this condition never occurs, for now.
        print_help()
        exit(-1)

if __name__ == '__main__':
    main()
