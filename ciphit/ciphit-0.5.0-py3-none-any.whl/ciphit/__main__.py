import click
from click_option_group import (
    optgroup, 
    MutuallyExclusiveOptionGroup,
    RequiredMutuallyExclusiveOptionGroup,
)
from rich import print
from ciphit.basemods.Ciphers import aes_cbc

def get_singleline(multi: list) -> repr:
    assert isinstance(multi,(list,str))
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
@optgroup.option(
    "--edit", 
    help="To edit Encrypted/Encoded files created by ciphit.", 
    is_flag=True, 
    flag_value=True,
)
@click.option(
        "-k","--key", 
        help="The key with which text is Encoded/Decoded.",
        default=False,
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
    
    if kwargs['edit']:
        if isFile or kwargs['key']:
            pass
        else:
            raise click.UsageError(
                "'--edit' flag is only allowed with '-f' / '--file'.\nhelp:\t'--edit'\n\t'-f' / '--file' [required]\n\t'-t' / '--text' [optional]"
            )

    if not kwargs['key']:
        kwargs['key'] = click.prompt('Key', 
                        hide_input=True, 
                        confirmation_prompt=True)

    if not kwargs['text'] and (not kwargs['edit'] and not isFile):
        print("[bold blue]Opening editor[/bold blue]")
        click.pause()
        kwargs['text']=click.edit(text='')
        if kwargs['text'] in (None,''):
            print("[bold red]error:[/bold red] Text is empty.")
            exit(1)
        kwargs['text']=kwargs['text'].strip('\n')

    if kwargs['edit']:
        deciphered = get_multiline(aes_cbc.PassDecode(kwargs['file'].read().strip(), kwargs['key']))
        kwargs['text']=click.edit(text=deciphered)
        if kwargs['text'] is None: exit(1)
        ciphered = aes_cbc.PassEncode(get_singleline(kwargs['text'].split('\n')), kwargs['key'])
        kwargs['file'].truncate(0)
        kwargs['file'].seek(0)
        kwargs['file'].write(ciphered)
    elif not kwargs['edit']:
        if not isFile:
            if kwargs['encode']:
                _ = aes_cbc.PassEncode(kwargs['text'],kwargs['key'])
                print(f"Final result: [bold yellow]{_}[/bold yellow]")
            else:#kwargs['decode']
                _ = aes_cbc.PassDecode(kwargs['text'],kwargs['key'])
                print(f"Final result: [bold green]{_}[/bold green]")
        elif isFile:
            if kwargs['encode']:
                _ = aes_cbc.PassEncode(get_singleline(kwargs['file'].readlines()), kwargs['key'])
                msg="[bold green]File is now enncrypted.[/bold green]"
            else:#kwargs['decode']
                _ = get_multiline(aes_cbc.PassDecode(kwargs['file'].read().strip(), kwargs['key']))
                msg="[bold green]File is now decrypted.[/bold green]"
            kwargs['file'].truncate(0)
            kwargs['file'].seek(0)
            kwargs['file'].write(_)
            print(msg)
        else:
            #this condition never occurs, for now.
            print_help()
            exit(1)

if __name__ == '__main__':
    main()
