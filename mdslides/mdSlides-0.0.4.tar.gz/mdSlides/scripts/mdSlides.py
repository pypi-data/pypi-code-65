from mdSlides import Engines
import click
import pathlib
import sys

@click.command()
@click.option("--engine","-e", default="pandoc:slidy", help="Slide engine to use.")
@click.option("--list-engines", is_flag=True, help="List available slide engines.")
@click.argument("input",type=click.Path(exists=True),nargs=-1)
def main(engine,list_engines,input):
  if list_engines:
    print("Available Engines")
    print("  pandoc:slidy")
    print("  pandoc:powerpoint")
    sys.exit(0)

  eng = None
  if engine.startswith("pandoc"):
    if engine.endswith(":slidy"):
        eng = Engines.PandocSlidy()
    if engine.endswith(":powerpoint") or engine.endswith(":ppt"):
        eng = Engines.PandocPowerPoint()

  if eng is None:
    print(f"Unreconized engine {engine}")
    sys.exit(1)

  for file in input:
    eng.build(click.format_filename(file))

