import click
from click_option_group import (
    optgroup,
    MutuallyExclusiveOptionGroup,
    RequiredMutuallyExclusiveOptionGroup,
)
from rich import print
from .basemods import Crypto


def print_help():
    ctx = click.get_current_context()
    click.echo(ctx.get_help())


@click.command()
@optgroup.group(
    "Encode/Decode",
    cls=RequiredMutuallyExclusiveOptionGroup,
)
@optgroup.option(
    "-e",
    "--encode",
    is_flag=True,
    flag_value=True,
)
@optgroup.option(
    "-d",
    "--decode",
    is_flag=True,
    flag_value=True,
)
@optgroup.option(
    "--edit",
    help="To edit Encrypted/Encoded files created by ciphit.",
    is_flag=True,
    flag_value=True,
)
@click.option(
    "-k",
    "--key",
    help="The key with which text is Encoded/Decoded.",
    default=False,
)
@optgroup.group(
    "Text/File",
    cls=MutuallyExclusiveOptionGroup,
)
@optgroup.option(
    "-t",
    "--text",
    help="The text you want to Encode/Decode.",
    default=False,
    type=str,
)
@optgroup.option(
    "-f",
    "--file",
    type=click.File("r+"),
    default=None,
)
def main(**kwargs):

    isFile = not kwargs["file"] is None

    if kwargs["edit"]:
        if isFile or kwargs["key"]:
            pass
        else:
            raise click.UsageError(
                "'--edit' flag is only allowed with '-f' / '--file'."
                "\nhelp:\t'--edit'\n\t'-f' / '--file' [required]\n\t'-t' / '--text' [optional]"
            )

    if not kwargs["key"]:
        kwargs["key"] = click.prompt("Key", hide_input=True, confirmation_prompt=True)

    if not kwargs["text"] and (not kwargs["edit"] and not isFile):
        print("[bold blue]Opening editor[/bold blue]")
        click.pause()
        kwargs["text"] = click.edit(text="")
        if kwargs["text"] in (None, ""):
            print("[bold red]error:[/bold red] Text is empty.")
            exit(1)
        kwargs["text"] = kwargs["text"].strip("\n")

    key_err = "[bold red]error:[/bold red] Invalid Key."

    if kwargs["edit"]:
        try:
            deciphered = Crypto.Aes_128_cbc_pass().decrypt(
                kwargs["file"].read().strip(), kwargs["key"]
            )
        except Exception:
            print(key_err)
            exit(1)
        kwargs["text"] = click.edit(text=deciphered)
        if kwargs["text"] is None:
            exit(1)
        ciphered = Crypto.Aes_128_cbc_pass().encrypt(kwargs["text"], kwargs["key"])
        kwargs["file"].truncate(0)
        kwargs["file"].seek(0)
        kwargs["file"].write(ciphered)
    elif not kwargs["edit"]:
        if not isFile:
            if kwargs["encode"]:
                _ = Crypto.Aes_128_cbc_pass().encrypt(kwargs["text"], kwargs["key"])
                print(f"Final result: [bold yellow]{_}[/bold yellow]")
            else:  # kwargs['decode']
                try:
                    _ = Crypto.Aes_128_cbc_pass().decrypt(kwargs["text"], kwargs["key"])
                except Exception:
                    print(key_err)
                    exit(1)
                print(f"Final result: [bold green]{_}[/bold green]")
        elif isFile:
            if kwargs["encode"]:
                _ = Crypto.Aes_128_cbc_pass().encrypt(
                    kwargs["file"].read(), kwargs["key"]
                )
                msg = "[bold green]File is now enncrypted.[/bold green]"
            else:  # kwargs['decode']
                try:
                    _ = Crypto.Aes_128_cbc_pass().decrypt(
                        kwargs["file"].read().strip(), kwargs["key"]
                    )
                except Exception:
                    print(key_err)
                    exit(1)
                msg = "[bold green]File is now decrypted.[/bold green]"
            kwargs["file"].truncate(0)
            kwargs["file"].seek(0)
            kwargs["file"].write(_)
            print(msg)
        else:
            # this condition never occurs, for now.
            print_help()
            exit(1)
