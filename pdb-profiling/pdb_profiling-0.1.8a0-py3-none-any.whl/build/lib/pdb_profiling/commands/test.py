import click
from pathlib import Path


def colorClick(name: str, template: str = "Initializing %s", fg: str = "green"):
    return click.style(template % name, fg=fg)


@click.group(chain=True, invoke_without_command=False)
@click.option("--folder", help="The file folder of new files.", type=click.Path())
@click.pass_context
def UniProt(ctx, folder):
    click.echo(colorClick("Folder"))
    folder = Path(folder)
    ctx.ensure_object(dict)
    ctx.obj['folder'] = folder
    for sub in ('mapping', 'fasta'):
        cur_path = folder/'UniProt'/sub
        cur_path.mkdir(parents=True, exist_ok=True)
        ctx.obj[f'{sub}_folder'] = cur_path
        click.echo(cur_path)


@UniProt.resultcallback()
@click.pass_context
def process_pipeline(ctx, processors, folder):
    click.echo(ctx.obj)
    click.echo(processors)


@UniProt.command("idmapping")
@click.option('--outname', type=str, help="the filename stem of output files", default="unp_yourlist")
@click.pass_context
def idMapping(ctx, outname):
    click.echo(colorClick("UniProt Retrieve/ID Mapping"))
    click.echo(outname)
    return "idmapping"


@UniProt.command("downloadseq")
@click.option('--outname', type=str, help="the filename stem of output files", default="unp_yourlist")
@click.pass_context
def downloadseq(ctx, outname):
    click.echo(colorClick("UniProt Sequence Download"))
    click.echo(outname)
    return 


if __name__ == '__main__':
    UniProt(obj={})
